# Анонсы первого релиза

Тексты подготовлены автором проекта для размещения от своего имени.
Наличие черновика в этом файле не означает, что он опубликован на площадке.
Используйте актуальные правила выбранного сообщества и раскрывайте своё
участие в проекте. Ссылки ведут на исходники и первый релиз.

## Reddit: weekly self-promotion thread

Disclosure: I maintain Local Agent Bridge, an MIT-licensed Python tool for
handing work from a local assistant such as Codex to OpenCode.

The workflow is a UTF-8 task file -> a separate OpenCode run -> a task ID with
start/exit status. A shared local board keeps handoffs, blockers and notes in
one place. It is for assistants that already have terminal access on the PC.

The bridge has no call quota or task-launch cap. Your model/client limits still
apply. Windows/Linux CI covers Python 3.10 and 3.13. There is also a reproducible
offline demo using a Python test executor, so you can check the handoff without
calling a model.

Code, setup and demo: https://github.com/pulvasnecov-hash/local-agent-bridge
First release: https://github.com/pulvasnecov-hash/local-agent-bridge/releases/tag/v0.1.0

I am looking for first-run feedback: did setup work, did your first handoff
complete, and what was confusing? Please include your OS if you try it.

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
