# Local Agent Bridge v0.1.0

First public release of a small, MIT-licensed bridge for local AI assistants
that hand tasks to OpenCode. The bridge itself has no subscription, monthly
call quota or cap on task launches. Your model and AI-client limits still apply.

## Included

- UTF-8 task-file handoff to a separate `opencode run --standalone` process.
- Task IDs and an append-only local board for status, results and handoffs.
- Configurable model, working directory and optional timeout.
- Windows launchers and an installer that preserves existing local settings.
- Russian/English documentation and first-run feedback forms.
- A reproducible offline demo plus GIF and MP4 playback.

## Try the offline demo

```text
python examples/offline_demo.py
```

It runs the real bridge CLI with a local Python test executor. The demo verifies
the output artifact (`27 × 14 = 378`) and the task records. It does not call an
LLM or require an OpenCode account. The MP4/GIF replays real command output;
pacing is edited for readability. It is a transport demo, not a model benchmark.

For real OpenCode execution, follow the README and use your existing provider
configuration. A successful process exit alone does not prove task correctness.

## Validation

CI runs the test suite and offline demo on Windows/Linux with Python 3.10/3.13.
The MP4 is H.264/yuv420p; the source package contains no local settings or logs.
Release attachments include a source ZIP, demo video, transcript and SHA-256 sums.

## Feedback

Please report whether installation and your first handoff worked using
[GitHub Issues](https://github.com/pulvasnecov-hash/local-agent-bridge/issues/new/choose).
Russian and English are welcome.

## По-русски

Первый релиз бесплатного локального моста Codex → OpenCode. Есть передача
UTF-8 заданий, метки задач, общая доска и воспроизводимое демо без вызова модели.
Скачайте ZIP, прочитайте README и сообщите, что получилось при первом запуске.
Лицензия MIT. Условия выбранной модели и ИИ-клиента сохраняются.
