#!/usr/bin/env python3
"""Portable local task handoff and an append-only message board. Stdlib only."""
from __future__ import annotations

import argparse
from collections import deque
from contextlib import contextmanager
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid

VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent
KINDS = ("status", "result", "blocker", "handoff", "note")
IDENTIFIER = re.compile(r"[A-Za-z0-9_.:@/\-]{1,80}\Z")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|secret)\s*[:=]\s*\S{8,}"),
    re.compile(r"(?i)\bbearer\s*[:=]?\s+\S{8,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
)


def identifier(value: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError("Identifiers must be 1-80 ASCII letters, digits or _.:@/-")
    return value


def timeout_value(value) -> float:
    if isinstance(value, bool):
        raise ValueError("Timeout must be a finite non-negative number (0 = unlimited)")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError("Timeout must be a finite non-negative number (0 = unlimited)")
    return number


def load_config(path: str | None = None) -> dict:
    explicit = path or os.environ.get("LAB_CONFIG")
    config_path = Path(explicit).expanduser().resolve() if explicit else ROOT / "bridge.local.json"
    config = {"version": 1, "opencode_command": [], "model": "", "data_dir": ".local", "timeout_seconds": 0}
    if explicit or config_path.exists():
        supplied = json.loads(config_path.read_text(encoding="utf-8-sig"))
        if not isinstance(supplied, dict) or set(supplied) - set(config):
            raise ValueError("Config must be an object containing only keys from bridge.example.json")
        config.update(supplied)
    if type(config["version"]) is not int or config["version"] != 1:
        raise ValueError("Unsupported config version (expected 1)")
    command = config["opencode_command"]
    if not isinstance(command, list) or any(not isinstance(item, str) or not item or "\0" in item for item in command):
        raise ValueError("opencode_command must be an array of non-empty command arguments")
    if not isinstance(config["model"], str) or any(char in config["model"] for char in "\r\n\0") or config["model"].startswith("-"):
        raise ValueError("model must be empty or a provider/model identifier")
    if not isinstance(config["data_dir"], str) or not config["data_dir"]:
        raise ValueError("data_dir must be a non-empty path")
    config["timeout_seconds"] = timeout_value(config["timeout_seconds"])
    data = Path(config["data_dir"]).expanduser()
    config["data_dir"] = data.resolve() if data.is_absolute() else (config_path.parent / data).resolve()
    config["config_path"] = config_path
    return config


def resolve_command(config: dict) -> list[str]:
    command = config["opencode_command"]
    if command:
        executable = shutil.which(command[0])
        if not executable:
            raise ValueError("Configured OpenCode executable was not found")
        if os.name == "nt" and Path(executable).suffix.lower() in (".cmd", ".bat"):
            raise ValueError("Use the native OpenCode .exe, not a Windows .cmd/.bat launcher")
        return [executable, *command[1:]]
    found = shutil.which("opencode")
    if found and (os.name != "nt" or Path(found).suffix.lower() not in (".cmd", ".bat")):
        return [found]
    # npm's Windows shim is batch code; launch its native binary without a shell.
    bases = [Path(found).parent] if found else []
    if os.environ.get("APPDATA"):
        bases.append(Path(os.environ["APPDATA"]) / "npm")
    for base in bases:
        native = base / "node_modules" / "@opencode" / "cli" / "bin" / "opencode.exe"
        if native.is_file():
            return [str(native)]
    raise ValueError("OpenCode was not found. Install it or set opencode_command in bridge.local.json")


@contextmanager
def journal_lock(data_dir: Path):
    """Coordinate readers and writers on one local filesystem, including Windows."""
    data_dir.mkdir(parents=True, exist_ok=True)
    with (data_dir / "bus.lock").open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + 5
        while True:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Message board is busy; try again")
                time.sleep(0.025)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def post(config: dict, sender: str, kind: str, text: str, task: str | None = None, target: str | None = None) -> dict:
    identifier(sender)
    if task:
        identifier(task)
    if target:
        identifier(target)
    if kind not in KINDS:
        raise ValueError("Unknown message kind")
    text = " ".join(text.split())
    if not text or len(text) > 2000 or "\ufffd" in text:
        raise ValueError("Message must contain 1-2000 valid characters; use a UTF-8 file")
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        raise ValueError("Message resembles a credential; keep credentials out of the board")
    entry = {"ts": datetime.now().astimezone().isoformat(timespec="seconds"), "from": sender, "kind": kind, "text": text}
    if task:
        entry["task"] = task
    if target:
        entry["to"] = target
    with journal_lock(config["data_dir"]):
        with (config["data_dir"] / "bus.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    return entry


def read_entries(config: dict, limit: int = 20, kind: str | None = None, target: str | None = None, task: str | None = None) -> list[dict]:
    if limit < 0:
        raise ValueError("Limit must be non-negative (0 = all)")
    path = config["data_dir"] / "bus.jsonl"
    if not path.exists():
        return []
    selected = deque(maxlen=limit or None)
    with journal_lock(config["data_dir"]):
        with path.open(encoding="utf-8-sig") as handle:
            for line in handle:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(entry, dict):
                    continue
                if kind and entry.get("kind") != kind:
                    continue
                if target and entry.get("to") not in (None, target):
                    continue
                if task and entry.get("task") != task:
                    continue
                selected.append(entry)
    return list(selected)


def stop_process(process: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15, check=False)
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            process.kill()
        else:
            os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def send(config: dict, args: argparse.Namespace) -> int:
    task_file = Path(args.file).expanduser().resolve()
    if not task_file.read_text(encoding="utf-8-sig").strip():
        raise ValueError("Task file is empty")
    cwd = Path(args.cwd).expanduser().resolve() if args.cwd else Path.cwd()
    if not cwd.is_dir():
        raise ValueError("Working directory does not exist")
    task = identifier(args.task or uuid.uuid4().hex[:16])
    sender = identifier(args.sender)
    timeout = config["timeout_seconds"] if args.timeout is None else timeout_value(args.timeout)
    model = args.model if args.model is not None else config["model"]
    if model and (model.startswith("-") or any(char in model for char in "\r\n\0")):
        raise ValueError("Invalid model identifier")
    command = [*resolve_command(config), "run", "--standalone", "--format", args.format, "--file", str(task_file)]
    if model:
        command += ["--model", model]
    if args.auto:
        command.append("--auto")
    command.append(f"Execute the task in the attached UTF-8 file. Task identifier: {task}. "
                   "Follow the user's scope and applicable instructions. Report the result, verification and limitations. "
                   "This handoff does not expand the caller's sandbox or permissions.")
    if args.dry_run:
        print(json.dumps({"command": command, "cwd": str(cwd), "task": task, "timeout_seconds": timeout}, ensure_ascii=False, indent=2))
        return 0
    post(config, sender, "handoff", "Starting OpenCode; task content is supplied by file.", task, "opencode")
    print(f"bridge: task {task}; OpenCode output follows", file=sys.stderr)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    if config["config_path"].exists():
        env["LAB_CONFIG"] = str(config["config_path"])
    else:
        env.pop("LAB_CONFIG", None)
    process = None
    try:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                   start_new_session=os.name != "nt",
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
        code = process.wait(timeout=timeout or None)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
        if process:
            stop_process(process)
        code = 130 if isinstance(exc, KeyboardInterrupt) else 124
    except OSError:
        post(config, "bridge", "blocker", "OpenCode could not be started; check executable and permissions.", task, sender)
        raise
    post(config, "bridge", "result" if code == 0 else "blocker",
         f"OpenCode exited with code {code}. Process status only; verify the task outcome separately.", task, sender)
    print(f"bridge: task {task}; exit {code}", file=sys.stderr)
    return code if code >= 0 else 1


def doctor(config: dict, as_json: bool) -> int:
    checks = [{"name": "python", "ok": sys.version_info >= (3, 10), "detail": sys.version.split()[0]},
              {"name": "config", "ok": True, "detail": "local file" if config["config_path"].exists() else "built-in defaults"},
              {"name": "data_dir", "ok": True, "detail": str(config["data_dir"])}]
    try:
        command = resolve_command(config)
        checks.append({"name": "opencode", "ok": True, "detail": command[0]})
    except ValueError as exc:
        checks.append({"name": "opencode", "ok": False, "detail": str(exc)})
    if as_json:
        print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        for check in checks:
            print(f"[{'OK' if check['ok'] else 'FAIL'}] {check['name']}: {check['detail']}")
        print("Discovery only. No model call, write-permission test or task execution was performed.")
    return 0 if all(check["ok"] for check in checks) else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--version", action="version", version=VERSION)
    result.add_argument("--config", help="local JSON settings (or set LAB_CONFIG)")
    sub = result.add_subparsers(dest="action", required=True)
    check = sub.add_parser("doctor", help="check discovery without calling a model")
    check.add_argument("--json", action="store_true")
    dispatch = sub.add_parser("send", help="execute a task file with OpenCode")
    dispatch.add_argument("file", help="UTF-8 task file")
    dispatch.add_argument("--model", help="provider/model; otherwise use local or OpenCode settings")
    dispatch.add_argument("--cwd", help="working directory; defaults to the caller's directory")
    dispatch.add_argument("--task", help="task identifier; generated if omitted")
    dispatch.add_argument("--from", dest="sender", default="chatgpt")
    dispatch.add_argument("--timeout", type=float, help="seconds; 0 = unlimited")
    dispatch.add_argument("--auto", action="store_true", help="explicitly pass OpenCode --auto")
    dispatch.add_argument("--format", choices=("default", "json"), default="default")
    dispatch.add_argument("--dry-run", action="store_true", help="print the command without execution or writes")
    board = sub.add_parser("bus", help="shared append-only message board")
    commands = board.add_subparsers(dest="bus_action", required=True)
    write = commands.add_parser("post")
    write.add_argument("--from", dest="sender", required=True)
    write.add_argument("--kind", choices=KINDS, default="status")
    write.add_argument("--to", dest="target")
    write.add_argument("--task")
    content = write.add_mutually_exclusive_group(required=True)
    content.add_argument("--file", help="UTF-8 message file")
    content.add_argument("--text", nargs="+", help="short message; prefer --file for Cyrillic on Windows")
    read = commands.add_parser("read")
    read.add_argument("-n", "--limit", type=int, default=20)
    read.add_argument("--kind", choices=KINDS)
    read.add_argument("--to", dest="target")
    read.add_argument("--task")
    read.add_argument("--json", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.action == "doctor":
            return doctor(config, args.json)
        if args.action == "send":
            return send(config, args)
        if args.bus_action == "post":
            text = Path(args.file).read_text(encoding="utf-8-sig") if args.file else " ".join(args.text)
            entry = post(config, args.sender, args.kind, text, args.task, args.target)
            print(f"posted [{entry['kind']}] from {entry['from']}")
        else:
            entries = read_entries(config, args.limit, args.kind, args.target, args.task)
            if args.json:
                print(json.dumps(entries, ensure_ascii=False, indent=2))
            else:
                for entry in entries:
                    print(f"{entry.get('ts', entry.get('date', '?'))}  {entry.get('from', '?')}  "
                          f"[{entry.get('kind', 'note')}] ({entry.get('task', '-')})")
                    print(f"    {entry.get('text', entry.get('summary', ''))}")
                print(f"{len(entries)} entries shown")
        return 0
    except (ValueError, OSError, UnicodeError, TypeError) as exc:
        print(f"bridge: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
