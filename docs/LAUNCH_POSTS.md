# Анонсы первого релиза

Тексты подготовлены автором проекта для размещения от своего имени.
Наличие черновика в этом файле не означает, что он опубликован на площадке.
Используйте актуальные правила выбранного сообщества и раскрывайте своё
участие в проекте. Ссылки ведут на исходники и первый релиз.

## Reddit: weekly self-promotion thread

Disclosure: I maintain Local Agent Bridge, a small MIT-licensed tool for local
Codex-to-OpenCode task handoffs.

It is for people who already use a local AI assistant with terminal access and
want it to pass work to OpenCode. A UTF-8 task file starts a separate OpenCode
run. The bridge records a task ID, start and exit status, and provides a shared
message board for coordination between assistants.

The bridge itself has no subscription, monthly call quota or cap on task
launches. Model-provider and AI-client limits still apply. It uses Python's
standard library and is tested on Windows/Linux with Python 3.10 and 3.13.

The README includes a reproducible offline demo. It uses a local Python test
executor, not an LLM, so you can test the handoff without a provider account.
Regular task execution uses your existing OpenCode configuration.

Code: https://github.com/pulvasnecov-hash/local-agent-bridge
Release and demo video: https://github.com/pulvasnecov-hash/local-agent-bridge/releases/tag/v0.1.0

I would appreciate first-run feedback: did installation work, could you launch
your first task, and which part of the handoff was confusing?

## Discord: relevant OpenCode community channel

Sharing a project I maintain: **Local Agent Bridge** (MIT).

It lets a terminal-capable local assistant, such as Codex, hand a UTF-8 task
file to a separate `opencode run --standalone` process. It adds task IDs and
a local message board for status and handoffs. The bridge has no call quota;
your model/client limits still apply.

Windows/Linux CI is included, and there is a reproducible offline demo that
uses a Python test executor instead of calling a model.

https://github.com/pulvasnecov-hash/local-agent-bridge

Looking for installation feedback and examples of workflows this could help.

## Короткий анонс на русском

Выложил Local Agent Bridge: бесплатный мост для передачи задач от локального
ИИ-помощника в OpenCode. Есть метки задач и общая доска статусов, результатов
и передачи работы между агентами.

Python, MIT, Windows/Linux. Число запусков моста не ограничено; тарифы моделей
и клиентов сохраняются. В README есть демо, которое можно повторить без
вызова модели.

Нужна обратная связь по установке и первой задаче:
https://github.com/pulvasnecov-hash/local-agent-bridge

## Hacker News

Автоматическая публикация и сгенерированный текст для HN не готовились.
Его [правила](https://news.ycombinator.com/newsguidelines.html) требуют писать
публикации самостоятельно и запрещают автоматизированное размещение.
Если автор выберет эту площадку, ему следует лично описать собственный опыт
и участвовать в обсуждении; формат должен соответствовать
[Show HN](https://news.ycombinator.com/showhn.html).
