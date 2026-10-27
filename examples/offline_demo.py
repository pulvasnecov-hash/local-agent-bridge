#!/usr/bin/env python3
"""Run a real bridge handoff with a local test executor. No model or network calls."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXECUTOR = '''import json
from pathlib import Path
import sys

task = Path(sys.argv[sys.argv.index("--file") + 1])
request = json.loads(task.read_text(encoding="utf-8"))
left, right = request["values"]
result = {"operation": "multiply", "values": [left, right], "result": left * right}
Path("result.json").write_text(json.dumps(result, indent=2) + "\\n", encoding="utf-8")
print("Local Python test executor; no LLM was called.")
print(f"Created result.json: {left} x {right} = {left * right}")
'''


def run_demo() -> dict:
    with tempfile.TemporaryDirectory(prefix="local-agent-bridge-demo-") as folder:
        work = Path(folder).resolve()
        (work / "test_executor.py").write_text(EXECUTOR, encoding="utf-8")
        task = {"operation": "multiply", "values": [27, 14]}
        (work / "task.json").write_text(json.dumps(task, indent=2), encoding="utf-8")
        config = {"version": 1, "opencode_command": [sys.executable, str(work / "test_executor.py")],
                  "data_dir": "state", "timeout_seconds": 15}
        settings = work / "demo.json"
        settings.write_text(json.dumps(config), encoding="utf-8")
        env = dict(os.environ, LAB_CONFIG=str(settings), PYTHONUTF8="1")

        def execute(*arguments):
            result = subprocess.run([sys.executable, str(ROOT / "bridge.py"), *arguments],
                                    cwd=work, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, encoding="utf-8", timeout=30)
            if result.returncode:
                raise RuntimeError(f"Demo step failed with code {result.returncode}: {result.stdout}")
            return result.stdout.replace(str(work), "<demo>").replace(sys.executable, "<python>")

        handoff = execute("send", str(work / "task.json"), "--task", "offline-demo")
        artifact = json.loads((work / "result.json").read_text(encoding="utf-8"))
        board = execute("bus", "read", "--task", "offline-demo", "--json")
        entries = json.loads(board)
        if artifact.get("result") != 378:
            raise RuntimeError("The output artifact did not contain the expected result")
        if [entry["kind"] for entry in entries] != ["handoff", "result"]:
            raise RuntimeError("The expected handoff/result records were not found")
        return {
            "mode": "offline-test-executor", "model_calls": False,
            "verified_result": artifact["result"], "records": len(entries),
            "steps": [
                {"title": "Prepare a task", "command": "Write task.json",
                 "output": json.dumps(task, indent=2)},
                {"title": "Hand off through the real bridge",
                 "command": "python bridge.py --config demo.json send task.json --task offline-demo",
                 "output": handoff.strip()},
                {"title": "Verify the output file", "command": "Read result.json",
                 "output": json.dumps(artifact, indent=2) + "\n\nVerified: 27 x 14 = 378"},
                {"title": "Inspect the shared board", "command": "python bridge.py bus read --task offline-demo",
                 "output": "\n".join(f"[{e['kind']}] task={e['task']}\n  {e['text']}" for e in entries)},
            ],
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the verified transcript as JSON")
    args = parser.parse_args()
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    report = run_demo()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("OFFLINE TRANSPORT DEMO: local test executor, no model or network calls.\n")
        for step in report["steps"]:
            print(f"$ {step['command']}\n{step['output']}\n")
        print("PASS: output artifact and both task records independently verified.")


if __name__ == "__main__":
    main()
