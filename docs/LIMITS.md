# Бесплатно и без лимитов: точный смысл

## Что бесплатно

Local Agent Bridge распространяется по лицензии MIT. За сам мост нет платы,
подписки, регистрации в сервисе моста или покупки пакетов вызовов.
Он использует стандартную библиотеку Python, локальные файлы и установленный
OpenCode. Собственный облачный сервис для работы моста не требуется.

## Каких квот нет

- Нет месячной или дневной квоты вызовов моста.
- Нет счётчика платных tool calls, кредитов моста или платных уровней доступа.
- Нет установленного мостом ограничения количества запусков задач.
- По умолчанию нет ограничения времени задачи: `timeout_seconds` равен `0`.
  При необходимости пользователь задаёт свой тайм-аут.

## Что сохраняется

Выбранный ИИ-клиент, OpenCode, провайдер модели и ваша подписка могут иметь
собственные квоты, ограничения и стоимость. Мост не отменяет их и не оплачивает
использование модели. Существуют также ограничения памяти, диска, прав доступа
и операционной системы.

Одна короткая запись в общей доске ограничена 2000 символами для удобства
координации. Большое задание передаётся отдельным UTF-8 файлом; лимит записи
доски к нему не применяется. Это ограничение формата, а не месячная квота.

Доступ к терминалу должен уже существовать в локальном помощнике.
Мост не расширяет разрешения и не предоставляет облачному чату удалённый доступ.

## Сравнение с Desktop Commander

Позиционирование проекта — бесплатная локальная альтернатива **Desktop Commander
Remote для передачи задач**, когда у помощника уже есть локальный терминал.
Маршрут не использует этот Remote-сервис и не расходует его квоту.

У самого Desktop Commander есть бесплатный открытый Local MCP без месячного
лимита. Его Remote MCP предлагает разные тарифы, включая вариант без месячной
квоты. Поэтому сравнение «весь Desktop Commander платный и ограниченный»
не соответствовало бы его документации.

Официальные источники, проверены 27.10.2026:
[Local и Remote MCP](https://desktopcommander.app/mcp/),
[тарифы и квоты](https://desktopcommander.app/pricing/).

Проект независимый и не связан с разработчиками Desktop Commander.

## English

The bridge itself is free under MIT: no bridge subscription, registration,
usage credits, monthly call quota or cap on task launches. Task runtime is
unlimited by default; an optional timeout is user-configured.

AI clients, OpenCode and model providers retain their own billing, quotas and
permission rules. Local hardware and operating-system limits still apply.
Board messages are limited to 2,000 characters; task files are separate.

The comparison covers a local task-handoff workflow for an assistant that
already has terminal access. This is an independent project, not a full
Desktop Commander replacement or a cloud-to-computer MCP server. Desktop
Commander's Local MCP is also free and has no monthly limit; Remote plans
are described on its official pricing page linked above.
