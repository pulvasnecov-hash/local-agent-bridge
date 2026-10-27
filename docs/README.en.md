# Local Agent Bridge

[![Tests](https://github.com/pulvasnecov-hash/local-agent-bridge/actions/workflows/tests.yml/badge.svg)](https://github.com/pulvasnecov-hash/local-agent-bridge/actions/workflows/tests.yml)
[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![Platforms](https://img.shields.io/badge/Windows%20%7C%20Linux-tested-2ea44f)

**Hand work from Codex to OpenCode and keep execution in view.**

Local Agent Bridge connects terminal-capable AI assistants through task files
and a shared message board. Your assistant hands off a task, OpenCode runs it
on your computer, and the bridge records its start and exit code under one task ID.

**A free local alternative to Desktop Commander Remote for task handoff.
Bridge calls and task launches are unlimited.** The source is MIT-licensed.
Your assistant needs existing local terminal access. Model and AI-client
pricing and usage limits still apply.

**[Download source](https://github.com/pulvasnecov-hash/local-agent-bridge/archive/refs/heads/main.zip)** ·
[Release v0.1.0](https://github.com/pulvasnecov-hash/local-agent-bridge/releases/tag/v0.1.0) ·
[Quick start](#quick-start) · [Русская документация](../README.md) ·
[Agent instructions](AGENT_INSTRUCTIONS.md)

## Watch a task handoff

![Reproducible offline task handoff](../assets/demo.gif)

This demo runs the real bridge CLI with a local Python test executor instead
of a model. It verifies the generated artifact and the board records separately.
Reproduce it with `python examples/offline_demo.py`.
[How the demo works](DEMO.md).

## What you get

| Goal | What the bridge provides |
|---|---|
| Delegate a task | A UTF-8 task file passed to a separate OpenCode run |
| Track execution | One task ID linking the start, exit code and failure status |
| Coordinate assistants | A shared board for status, results and handoffs |
| Work at your own pace | Unlimited bridge calls and an optional task timeout |
| Move to another computer | A self-contained folder using the Python standard library |

The board stays on your disk. The bridge itself needs no hosted service.
Model execution uses your chosen OpenCode provider. Windows and Linux are tested.

## Quick start

Install Python 3.10+ and OpenCode, sign in to your provider, then:

```powershell
git clone https://github.com/pulvasnecov-hash/local-agent-bridge.git
cd local-agent-bridge
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
.\bridge.cmd send .\examples\task.txt --dry-run
```

The last command previews the task launch. Remove `--dry-run` to execute it
using your existing OpenCode account and plan. You can also
[download a ZIP](https://github.com/pulvasnecov-hash/local-agent-bridge/archive/refs/heads/main.zip).

## Requirements

- Python 3.10 or newer; standard library only.
- OpenCode installed and authenticated with your chosen provider.
- A local assistant already authorized to execute commands on this computer.

This integration uses the standard [OpenCode CLI](https://opencode.ai/v2/docs/cli).

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

## How it compares to Desktop Commander

The bridge suits local assistants that already read files and run commands.
Task handoff goes directly to OpenCode, so Desktop Commander Remote call quotas
are not involved in this route.

Desktop Commander's Local MCP is also free and has no monthly limit.
See its [official connection options](https://desktopcommander.app/mcp/)
and [pricing](https://desktopcommander.app/pricing/), checked October 27, 2026.

A cloud chat needs an appropriate remote-access channel or MCP server.
Local Agent Bridge provides local task handoff and a coordination board.
Conversation history, credentials and tool sessions are not transferred between
applications. The comparison covers this local workflow.

Read [what free and unlimited means](LIMITS.md) and
[the security boundaries](../SECURITY.md).

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

## Help test the first run

Did installation and your first handoff work? Tell us what was confusing and
which workflow you tried. [Share feedback or report a bug](https://github.com/pulvasnecov-hash/local-agent-bridge/issues/new/choose).
Russian and English are welcome.
