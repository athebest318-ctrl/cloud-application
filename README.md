# Cloud Application

Учебный проект по дисциплине «Управление работами и разработка программного
обеспечения облачных систем». Проект объединяет результаты лабораторных работ
1-19: FastAPI, REST API, OpenAPI, модульную архитектуру, Git-процесс,
конфигурацию окружения, PostgreSQL, SQLAlchemy, Alembic, валидацию,
объектное хранилище и учебную аутентификацию.

## Возможности

- CRUD для облачных сервисов с фильтрацией по состоянию;
- хранение сервисов, пользователей, сеансов и метаданных объектов в PostgreSQL;
- миграции схемы через Alembic;
- загрузка, скачивание и удаление файлов из локального объектного хранилища;
- регистрация, вход, проверка и завершение сеансов;
- Swagger UI, ReDoc и схема OpenAPI;
- автоматические тесты и скрипт комплексной проверки.

## Подготовка

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

В `.env` укажите параметры своей PostgreSQL. По умолчанию проект ожидает базу
`cloud_application` и пользователя `cloud_app`.

```powershell
alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

После запуска доступны:

- приложение: `http://127.0.0.1:8000/`;
- Swagger UI: `http://127.0.0.1:8000/docs`;
- ReDoc: `http://127.0.0.1:8000/redoc`;
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`.

## API

- `GET /status`, `/about`, `/course`, `/service-count` - системные маршруты;
- `GET|POST /services` - список, фильтрация и создание сервисов;
- `GET|PUT|DELETE /services/{service_id}` - работа с отдельным сервисом;
- `GET|POST /objects` - список и загрузка объектов;
- `GET /objects/{object_id}/download` - скачивание объекта;
- `DELETE /objects/{object_id}` - удаление объекта;
- `POST /auth/register`, `/auth/login` - регистрация и вход;
- `GET /auth/session/{token}` - проверка сеанса;
- `DELETE /auth/session/{token}` - завершение сеанса.

## Структура проекта

- `app/routers/` - HTTP-маршруты;
- `app/schemas/` - Pydantic-схемы и валидация;
- `app/services/` - бизнес-логика;
- `app/data/` - SQLAlchemy-модели и подключение к базе;
- `migrations/` - миграции Alembic;
- `docs/sql/` - SQL-сценарии лабораторных работ;
- `tests/` - автоматические проверки;
- `reports/` - отчёты по лабораторным работам;
- `evidence/` - сохранённые результаты комплексной проверки.

## Состояния сервисов

- `running` - сервис работает;
- `maintenance` - сервис находится на обслуживании;
- `stopped` - сервис остановлен.

## Проверка

```powershell
pytest -q
alembic check
python scripts/verify_project.py
```

## Работа с проектом

Основная ветка - `main`. Изменения выполняются в тематических ветках,
проверяются тестами и объединяются через pull request. История репозитория
содержит отдельные ветки для настройки приложения и фильтрации сервисов.

> Аутентификация в лабораторной работе 19 является учебной: пароли сохраняются
> без промышленного хеширования. Такой механизм нельзя использовать в реальном
> приложении.
