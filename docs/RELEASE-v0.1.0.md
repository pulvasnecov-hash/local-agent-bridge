# Local Agent Bridge v0.1.0

**Hand a task from Codex to OpenCode. Keep the execution trail on your own computer.**

Local Agent Bridge gives terminal-capable AI assistants a repeatable handoff:
send a UTF-8 task file to OpenCode, follow its output, and inspect the start and
exit status under one task ID. A shared local board helps assistants coordinate
their work.

**Free under MIT, with unlimited bridge calls and task launches.** Existing
AI-client and model-provider pricing and limits still apply.

![Reproducible task handoff](https://github.com/pulvasnecov-hash/local-agent-bridge/releases/download/v0.1.0/demo.gif)

[Download the source ZIP](https://github.com/pulvasnecov-hash/local-agent-bridge/releases/download/v0.1.0/local-agent-bridge-0.1.0.zip)
· [Watch the 42-second demo](https://github.com/pulvasnecov-hash/local-agent-bridge/releases/download/v0.1.0/local-agent-bridge-demo.mp4)
· [English documentation](https://github.com/pulvasnecov-hash/local-agent-bridge/blob/main/docs/README.en.md)
· [Документация на русском](https://github.com/pulvasnecov-hash/local-agent-bridge#readme)

## Use it when

- Your local assistant plans a task and you want OpenCode to execute it in a chosen working directory.
- Several assistants need a shared place for status, handoffs and blockers.
- You want a small local integration you can inspect, copy and configure yourself.

## Included

- UTF-8 task-file handoff to a separate `opencode run --standalone` process.
- Task IDs and an append-only local board for status, results and handoffs.
- Configurable model, working directory and optional timeout.
- Windows launchers and an installer that preserves existing local settings.
- Russian/English documentation and first-run feedback forms.
- A reproducible offline demo plus GIF and MP4 playback.

## Try the offline demo

Clone the project or extract the source ZIP, then run:

```text
git clone https://github.com/pulvasnecov-hash/local-agent-bridge.git
cd local-agent-bridge
python examples/offline_demo.py
```

It runs the real bridge CLI with a local Python test executor. The demo verifies
the output artifact (`27 × 14 = 378`) and the task records. It does not call an
LLM or require an OpenCode account. The MP4/GIF replays real command output;
pacing is edited for readability. It is a transport demo, not a model benchmark.

For real OpenCode execution, follow the README and use your existing provider
configuration. A successful process exit alone does not prove task correctness.

## Validation

The test suite and offline demo passed on Windows/Linux with Python 3.10/3.13.
[View the successful release-commit CI](https://github.com/pulvasnecov-hash/local-agent-bridge/actions/runs/40573681864).
The MP4 is H.264/yuv420p; the source package contains no local settings or logs.
Release attachments include a source ZIP, demo video, transcript and SHA-256 sums.

## Hand a real task to OpenCode

With OpenCode installed and signed in to your provider:

```text
python bridge.py send examples/task.txt --dry-run
python bridge.py send examples/task.txt --task first-handoff
python bridge.py bus read --task first-handoff
```

Use your own task file and `--cwd` to select a working directory. The runtime
uses Python's standard library. Windows launchers and a local config installer
are included. Your assistant needs existing authorized terminal access.

## Choose your download

| Attachment | Contents |
|---|---|
| `local-agent-bridge-0.1.0.zip` | Source, launchers, examples, documentation and tests |
| `local-agent-bridge-demo.mp4` | 42-second offline transport demo |
| `demo.gif` | Lightweight animated preview |
| `demo-transcript.json` | Captured commands, output and verification results |
| `SHA256SUMS.txt` | SHA-256 checksums for the attachments |

## Feedback

**Tried your first handoff?** Tell us your OS, whether setup worked, and the step
that was unclear using
[GitHub Issues](https://github.com/pulvasnecov-hash/local-agent-bridge/issues/new/choose).
Russian and English are welcome.

## По-русски

Первый релиз бесплатного локального моста Codex → OpenCode. Есть передача
UTF-8 заданий, метки задач, общая доска и воспроизводимое демо без вызова модели.
Скачайте ZIP, прочитайте README и сообщите, что получилось при первом запуске.
Лицензия MIT. Условия выбранной модели и ИИ-клиента сохраняются.
