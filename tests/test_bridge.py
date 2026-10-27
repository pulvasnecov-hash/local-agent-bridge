"""Exercise real CLI/process boundaries with a local fake executor, never a model."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import bridge

ROOT = Path(__file__).resolve().parents[1]


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lab test ")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name).resolve()
        self.config_file = self.directory / "settings.json"
        self.capture = self.directory / "capture.json"
        self.fake = self.directory / "fake executor.py"
        self.fake.write_text(
            "import json, os, pathlib, sys, time\n"
            "mode = sys.argv[1]\n"
            "pathlib.Path(os.environ['LAB_TEST_CAPTURE']).write_text(json.dumps({\n"
            "    'args': sys.argv[2:], 'cwd': os.getcwd(), 'stdin': sys.stdin.read(),\n"
            "    'config': os.environ.get('LAB_CONFIG')\n"
            "}), encoding='utf-8')\n"
            "if mode == 'sleep': time.sleep(60)\n"
            "sys.exit(7 if mode == 'fail' else 0)\n", encoding="utf-8")
        self.task_file = self.directory / "Задание & пример.txt"
        self.task_file.write_text("Проверить связь. Ничего не публиковать.\n", encoding="utf-8-sig")
        self.write_config()
        self.config = bridge.load_config(str(self.config_file))
        self.env = dict(os.environ, LAB_CONFIG=str(self.config_file), LAB_TEST_CAPTURE=str(self.capture), PYTHONUTF8="1")

    def write_config(self, mode="ok", **overrides):
        config = {"version": 1, "opencode_command": [sys.executable, str(self.fake), mode], "data_dir": "state"}
        config.update(overrides)
        self.config_file.write_text(json.dumps(config), encoding="utf-8-sig")

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "bridge.py"), *args], env=self.env,
                              cwd=self.directory, capture_output=True, text=True, encoding="utf-8", timeout=30)

    def entries(self):
        return bridge.read_entries(self.config, limit=0)

    def test_config_relative_to_file_not_current_directory(self):
        self.assertEqual(self.config["data_dir"], self.directory / "state")
        self.assertFalse(self.config["data_dir"].exists())

    def test_missing_default_config_uses_defaults_without_writing(self):
        with patch.object(bridge, "ROOT", self.directory), patch.dict(os.environ, {}, clear=True):
            self.config_file.unlink()
            self.assertEqual(bridge.load_config()["opencode_command"], [])
            self.assertFalse((self.directory / ".local").exists())

    def test_invalid_configs_fail_cleanly(self):
        for invalid in ([], {"unexpected": 1}, {"version": 2}, {"version": True},
                        {"opencode_command": "opencode --auto"}, {"opencode_command": [""]},
                        {"data_dir": ""}, {"model": "--auto"}):
            with self.subTest(invalid=invalid):
                self.config_file.write_text(json.dumps(invalid), encoding="utf-8")
                result = self.cli("doctor")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_invalid_timeouts_are_rejected(self):
        for value in (-1, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bridge.timeout_value(value)

    def test_cyrillic_bom_file_through_compatibility_entrypoint(self):
        message = self.directory / "сообщение.txt"
        message.write_text("Связь работает.\nПеревірено.", encoding="utf-8-sig")
        result = subprocess.run([sys.executable, str(ROOT / "bus.py"), "post", "--from", "tester",
                                 "--file", str(message)], env=self.env, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.entries()[0]["text"], "Связь работает. Перевірено.")

    def test_credentials_and_bad_text_refused_before_creating_journal(self):
        for text in ("password: example", "api_key=example-value", "Bearer example-value",
                     "-----BEGIN PRIVATE KEY-----", "ghp_" + "a" * 30, "", "x" * 2001, "bad\ufffd"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                bridge.post(self.config, "tester", "note", text)
        self.assertFalse(self.config["data_dir"].exists())

    def test_identifiers_are_validated(self):
        for name in ("", "with space", "x" * 81, "agent\nspoofed"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                bridge.post(self.config, name, "note", "message")

    def test_filters_broadcast_and_order(self):
        bridge.post(self.config, "a", "handoff", "first", "one", "opencode")
        bridge.post(self.config, "b", "result", "second", "two", "other")
        bridge.post(self.config, "c", "note", "third", "one")
        self.assertEqual([x["text"] for x in bridge.read_entries(self.config, target="opencode", task="one")], ["first", "third"])
        self.assertEqual(bridge.read_entries(self.config, kind="result")[0]["text"], "second")
        self.assertEqual(bridge.read_entries(self.config, limit=1)[0]["text"], "third")
        with self.assertRaises(ValueError):
            bridge.read_entries(self.config, limit=-1)

    def test_foreign_and_malformed_entries_do_not_break_reading(self):
        directory = self.config["data_dir"]
        directory.mkdir()
        (directory / "bus.jsonl").write_text('broken\n[]\n{"summary":"legacy","date":"today"}\n', encoding="utf-8")
        self.assertEqual(self.entries(), [{"summary": "legacy", "date": "today"}])

    def test_concurrent_processes_do_not_lose_entries(self):
        def write(number):
            return self.cli("bus", "post", "--from", "tester", "--task", f"task-{number}", "--text", f"message {number}")
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(write, range(12)))
        self.assertTrue(all(x.returncode == 0 for x in results), [x.stderr for x in results])
        self.assertEqual({x["task"] for x in self.entries()}, {f"task-{i}" for i in range(12)})

    def test_send_preserves_literal_paths_closes_stdin_and_records_lifecycle(self):
        result = self.cli("send", str(self.task_file), "--task", "literal-path")
        self.assertEqual(result.returncode, 0, result.stderr)
        captured = json.loads(self.capture.read_text())
        self.assertEqual(captured["stdin"], "")
        self.assertEqual(captured["cwd"], str(self.directory))
        self.assertEqual(captured["config"], str(self.config_file))
        self.assertIn(str(self.task_file), captured["args"])
        self.assertIn("--standalone", captured["args"])
        self.assertNotIn("--auto", captured["args"])
        self.assertNotIn("--model", captured["args"])
        self.assertEqual([x["kind"] for x in self.entries()], ["handoff", "result"])
        self.assertEqual({x["task"] for x in self.entries()}, {"literal-path"})

    def test_explicit_model_auto_and_working_directory(self):
        work = self.directory / "work"
        work.mkdir()
        result = self.cli("send", str(self.task_file), "--auto", "--model", "example/model", "--cwd", str(work))
        self.assertEqual(result.returncode, 0, result.stderr)
        captured = json.loads(self.capture.read_text())
        self.assertIn("--auto", captured["args"])
        self.assertEqual(captured["args"][captured["args"].index("--model") + 1], "example/model")
        self.assertEqual(captured["cwd"], str(work))

    def test_default_settings_do_not_export_a_nonexistent_config(self):
        env = dict(self.env)
        env.pop("LAB_CONFIG")
        with patch.dict(os.environ, env, clear=True), patch.object(bridge, "ROOT", self.directory):
            config = bridge.load_config()
            args = bridge.parser().parse_args(["send", str(self.task_file)])
            with patch.object(bridge, "resolve_command", return_value=[sys.executable, str(self.fake), "ok"]), redirect_stderr(io.StringIO()):
                self.assertEqual(bridge.send(config, args), 0)
        captured = json.loads(self.capture.read_text())
        self.assertIsNone(captured["config"])
        self.assertEqual(len(bridge.read_entries(config)), 2)

    def test_failed_executor_returns_exit_code_and_blocker(self):
        self.write_config(mode="fail")
        result = self.cli("send", str(self.task_file))
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(self.entries()[-1]["kind"], "blocker")
        self.assertIn("code 7", self.entries()[-1]["text"])

    def test_timeout_stops_executor_and_records_blocker(self):
        self.write_config(mode="sleep")
        result = self.cli("send", str(self.task_file), "--timeout", "0.5")
        self.assertEqual(result.returncode, 124, result.stderr)
        self.assertEqual(self.entries()[-1]["kind"], "blocker")

    def test_dry_run_does_not_execute_or_write(self):
        result = self.cli("send", str(self.task_file), "--dry-run", "--task", "preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        preview = json.loads(result.stdout)
        self.assertEqual(preview["task"], "preview")
        self.assertIn(str(self.task_file), preview["command"])
        self.assertFalse(self.capture.exists())
        self.assertFalse(self.config["data_dir"].exists())

    def test_input_failure_does_not_dispatch(self):
        self.task_file.write_text(" ", encoding="utf-8")
        result = self.cli("send", str(self.task_file))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.capture.exists())
        self.assertFalse(self.config["data_dir"].exists())

    def test_doctor_is_discovery_only(self):
        result = self.cli("doctor", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(item["ok"] for item in json.loads(result.stdout)))
        self.assertFalse(self.capture.exists())
        self.assertFalse(self.config["data_dir"].exists())

    def test_missing_executable_is_reported_as_failure(self):
        self.write_config(opencode_command=[str(self.directory / "not-installed")])
        result = self.cli("doctor")
        self.assertEqual(result.returncode, 1)
        self.assertIn("[FAIL] opencode", result.stdout)

    @unittest.skipUnless(os.name == "nt", "Windows launchers")
    def test_windows_command_wrapper(self):
        result = subprocess.run(["cmd", "/d", "/c", str(ROOT / "bridge.cmd"), "doctor", "--json"],
                                env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(item["ok"] for item in json.loads(result.stdout)))

    @unittest.skipUnless(os.name == "nt", "Windows installer")
    def test_installer_keeps_existing_config(self):
        install_dir = self.directory / "установка с пробелами"
        install_dir.mkdir()
        for name in ("bridge.py", "bridge.example.json", "install.ps1"):
            shutil.copy2(ROOT / name, install_dir / name)
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        self.assertIsNotNone(powershell)
        for _ in range(2):
            result = subprocess.run([powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                                     str(install_dir / "install.ps1"), "-OpenCodeExecutable", sys.executable],
                                    env=self.env, capture_output=True, text=True, encoding="utf-8", timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = (install_dir / "bridge.local.json").read_bytes()
            if _ == 0:
                first = data
            else:
                self.assertEqual(data, first)


if __name__ == "__main__":
    unittest.main()
