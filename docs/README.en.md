# Local Agent Bridge

A small local bridge for handing UTF-8 task files from a terminal-capable
assistant to OpenCode, with an append-only message board for coordination.
Windows is the primary platform. The Python implementation also targets POSIX.

[Русская документация](../README.md) · [Security boundaries](../SECURITY.md)

## Requirements

- Python 3.10 or newer; standard library only.
- OpenCode installed and authenticated with your chosen provider.
- A local assistant already authorized to execute commands on this computer.

This integration uses the standard [OpenCode CLI](https://opencode.ai/v2/docs/cli).
It does not provide remote access to a cloud chat or connect to the assistant's
existing GUI conversation. Credentials, conversation history and tool sessions
are not transferred between applications.

## Setup

From the checkout on Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
.\bridge.cmd doctor
```

The installer creates `bridge.local.json` only if absent. Existing settings are
preserved. No service, startup entry, PATH change or dependency download is made.
`doctor` checks discovery only: it does not call a model or test provider access.

If needed, set `opencode_command` to an argument array such as
`["C:/Tools/OpenCode/opencode.exe"]`. Windows batch launchers are rejected so
task arguments can be passed without a shell. On POSIX, copy
`bridge.example.json` to `bridge.local.json` and use `python3 bridge.py`.

## Run a task

```powershell
.\bridge.cmd send .\examples\task.txt --dry-run
.\bridge.cmd send .\examples\task.txt --cwd 'C:\Work\Project' --task demo
.\bus.cmd read --task demo
```

The example task is in Russian; replace it with any UTF-8 task. OpenCode starts
with `run --standalone`, closed stdin and the attached file. Its output streams
to your terminal. A `handoff` and a final `result` or `blocker` record share the
same task identifier. Exit zero reports process completion, not verified task
correctness. Check the actual artifacts separately.

Options:

- `--model provider/model`: override the configured or OpenCode default model.
- `--timeout 300`: stop the process tree after 300 seconds; zero means unlimited.
- `--auto`: explicitly pass OpenCode's auto-approval flag; absent by default.
- `--format json`: stream OpenCode JSON output.
- `--dry-run`: display the command without execution or journal writes.

Model usage follows the existing OpenCode account, provider and billing plan.
The bridge does not change provider settings or expand the caller's permissions.
Exit codes: OpenCode's code; `2` for input/configuration errors, `124` for timeout,
and `130` for user interruption.

## Shared message board

```powershell
.\bus.cmd post --from codex --kind status --task demo --text "Starting verification"
.\bus.cmd read -n 20 --json
.\bus.cmd read --kind result --task demo
```

Kinds: `status`, `result`, `blocker`, `handoff`, `note`. Optional `--to` identifies
a recipient. It does not dispatch a task. Only `send` launches OpenCode.
Messages are limited to 2,000 characters; use `--file` for UTF-8 messages on Windows.
Writers and readers coordinate through a local file lock. Handoff messages are
advisory and do not lock working files. Network filesystems are unsupported.

The board is plaintext and sender identities are self-declared. Credential
heuristics reject some obvious secret patterns; they are not comprehensive.
Read [SECURITY.md](../SECURITY.md) before using private task data.

## Configuration

`bridge.example.json` documents all keys:

| Key | Default |
|---|---|
| `opencode_command` | `[]`: discover OpenCode; otherwise executable plus arguments |
| `model` | `""`: leave model selection to OpenCode |
| `data_dir` | `.local`, relative to the settings file |
| `timeout_seconds` | `0`: unlimited |

Use `python bridge.py --config settings.json <command>` or `LAB_CONFIG` to select
a shared config. The child inherits its absolute path. The task working directory
defaults to the caller's directory unless `--cwd` is supplied. Keep private task
files in the Git-ignored `private/` directory. Local config and journals are ignored.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests use a fake local executor, never a model. They cover real subprocess
handoffs, argument integrity, UTF-8, concurrent journal writes, errors, timeouts,
and Windows launch/install scripts. CI is configured for Windows/Linux with
Python 3.10/3.13; check Actions for its actual status.

This project packages a previously used local assistant-to-OpenCode workflow
without machine-specific paths or private logs. License: [MIT](../LICENSE).
