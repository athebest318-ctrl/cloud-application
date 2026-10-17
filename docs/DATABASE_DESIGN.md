# Проектирование базы данных Cloud Application

## Сущности

`ServiceType` хранит справочник типов сервисов. Один тип связан с несколькими
записями `Service`. `ServiceStatusHistory` фиксирует каждое состояние сервиса.
`StoredObject` хранит метаданные файлов, размещённых в `storage/objects`.
`User` связан отношением один ко многим с `AuthSession` и отношением многие к
одному с `Role`. Роль объединяет разрешения `Permission` через таблицу связи
`role_permissions`.

```text
ServiceType 1 ----- N Service 1 ----- N ServiceStatusHistory

StoredObject

User 1 ----- N AuthSession
Role 1 ----- N User
Role M ----- N Permission
```

## Ключи и ограничения

- первичные ключи: `id` во всех таблицах;
- внешние ключи: `services.type_id`, `service_status_history.service_id`,
  `auth_sessions.user_id`, `users.role_id`, а также оба ключа таблицы
  `role_permissions`;
- уникальные значения: имя типа, физическое имя файла, имя пользователя, токен,
  имя роли и код разрешения;
- допустимые состояния: `running`, `maintenance`, `stopped`;
- пустое имя типа запрещено проверкой `TRIM(name) <> ''`.

## Хранение файлов

Файл сохраняется на диске под UUID-именем. PostgreSQL хранит исходное имя,
внутреннее имя, MIME-тип, размер, путь и дату создания. API не возвращает
внутренний путь клиенту.

## Ролевая модель

`viewer` читает сервисы и объекты. `operator` дополнительно изменяет их.
`administrator` также управляет пользователями и ролями. Дополнительная роль
`content_manager` демонстрирует, что новые комбинации разрешений создаются как
данные без новой миграции. Миграция `007_access` создаёт таблицы `roles`,
`permissions`, `role_permissions` и поле `users.role_id`.
