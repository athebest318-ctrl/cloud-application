# Проектирование базы данных Cloud Application

## Сущности

`ServiceType` хранит справочник типов сервисов. Один тип связан с несколькими
записями `Service`. `ServiceStatusHistory` фиксирует каждое состояние сервиса.
`StoredObject` хранит метаданные файлов, размещённых в `storage/objects`.
`User` связан отношением один ко многим с `AuthSession`.

```text
ServiceType 1 ----- N Service 1 ----- N ServiceStatusHistory

StoredObject

User 1 ----- N AuthSession
```

## Ключи и ограничения

- первичные ключи: `id` во всех таблицах;
- внешние ключи: `services.type_id`, `service_status_history.service_id`,
  `auth_sessions.user_id`;
- уникальные значения: имя типа, физическое имя файла, имя пользователя, токен;
- допустимые состояния: `running`, `maintenance`, `stopped`;
- пустое имя типа запрещено проверкой `TRIM(name) <> ''`.

## Хранение файлов

Файл сохраняется на диске под UUID-именем. PostgreSQL хранит исходное имя,
внутреннее имя, MIME-тип, размер, путь и дату создания. API не возвращает
внутренний путь клиенту.
