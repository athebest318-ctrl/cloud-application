# Cloud Application

Учебный проект по дисциплине «Управление работами и разработка программного
обеспечения облачных систем». Проект объединяет результаты лабораторных работ
1-20: FastAPI, REST API, OpenAPI, модульную архитектуру, Git-процесс,
конфигурацию окружения, PostgreSQL, SQLAlchemy, Alembic, валидацию,
объектное хранилище, учебную аутентификацию и ролевую модель доступа.

## Возможности

- CRUD для облачных сервисов с фильтрацией по состоянию;
- хранение сервисов, пользователей, сеансов и метаданных объектов в PostgreSQL;
- миграции схемы через Alembic;
- загрузка, скачивание и удаление файлов из локального объектного хранилища;
- регистрация, вход, проверка и завершение сеансов;
- роли пользователей и эффективные разрешения через `/access`;
- Swagger UI, ReDoc и схема OpenAPI;
- автоматические тесты и скрипт комплексной проверки.

## Быстрый запуск в Windows PowerShell

Все команды выполняются из папки, в которой находятся `README.md` и
`requirements.txt`. Активация виртуального окружения не требуется: ниже везде
используется его `python.exe` напрямую, поэтому запрет запуска PowerShell-
сценариев не мешает работе.

### 1. Создание окружения

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Если команда `python` не найдена, используйте `py -m venv .venv`.

### 2. Настройка PostgreSQL

В pgAdmin должны существовать:

- сервер PostgreSQL, запущенный на `localhost:5432`;
- пользователь `cloud_app` с паролем;
- база `cloud_application`, владельцем которой является `cloud_app`.

Создайте локальный файл настроек и откройте его:

```powershell
Copy-Item .env.example .env
notepad .env
```

В строке `DATABASE_URL` замените `YOUR_PASSWORD` на пароль пользователя
`cloud_app`. Файл `.env` не публикуется в Git.

### 3. Подготовка таблиц и ролей

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.init_access
```

После второй команды должно появиться сообщение `Access model initialized`.

### 4. Запуск приложения

Рекомендуемый способ:

```powershell
.\run_windows.cmd
```

Скрипт использует порт `8010`, чтобы не конфликтовать с процессом на `8000`.
Эквивалентная команда без скрипта:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```

После запуска доступны:

- приложение: `http://127.0.0.1:8010/`;
- Swagger UI: `http://127.0.0.1:8010/docs`;
- ReDoc: `http://127.0.0.1:8010/redoc`;
- OpenAPI JSON: `http://127.0.0.1:8010/openapi.json`.

Чтобы выбрать другой порт, передайте его первым аргументом:

```powershell
.\run_windows.cmd 8020
```

## Решение частых ошибок

### Выполнение сценариев отключено

Ошибка относится только к `Activate.ps1`. Активация не обязательна: запускайте
команды через `.\.venv\Scripts\python.exe`, как показано выше.

Если активация всё же нужна, разрешите её только для текущего окна PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

После закрытия окна это разрешение сбросится.

### WinError 10013 при запуске Uvicorn

Порт может быть занят или зарезервирован Windows. Не запускайте второй сервер
на том же порту. Используйте подготовленный порт `8010`:

```powershell
.\run_windows.cmd 8010
```

Проверить, занят ли порт `8000`, можно так:

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

Если занят и `8010`, запустите `run_windows.cmd 8020`.

### Ошибка подключения к PostgreSQL

Проверьте, что сервер запущен в pgAdmin, пароль в `.env` указан без
`YOUR_PASSWORD`, а база называется `cloud_application`. Затем повторите:

```powershell
.\.venv\Scripts\python.exe -m alembic current
```

Ожидаемая ревизия после ЛР №20: `007_access (head)`.

## API

- `GET /status`, `/about`, `/course`, `/service-count` - системные маршруты;
- `GET|POST /services` - список, фильтрация и создание сервисов;
- `GET|PUT|DELETE /services/{service_id}` - работа с отдельным сервисом;
- `GET|POST /objects` - список и загрузка объектов;
- `GET /objects/{object_id}/download` - скачивание объекта;
- `DELETE /objects/{object_id}` - удаление объекта;
- `POST /auth/register`, `/auth/login` - регистрация и вход;
- `GET /auth/session/{token}` - проверка сеанса;
- `DELETE /auth/session/{token}` - завершение сеанса;
- `GET /access/roles` - роли и их разрешения;
- `GET /access/users/{user_id}` - роль и разрешения пользователя;
- `PUT /access/users/{user_id}/role` - назначение роли.

## Структура проекта

- `app/routers/` - HTTP-маршруты;
- `app/schemas/` - Pydantic-схемы и валидация;
- `app/services/` - бизнес-логика;
- `app/data/` - SQLAlchemy-модели и подключение к базе;
- `migrations/` - миграции Alembic;
- `docs/sql/` - SQL-сценарии лабораторных работ;
- `tests/` - автоматические проверки;
- `reports/` - отчёты по лабораторным работам;
- `evidence/` - сохранённые результаты комплексной проверки;
- `scripts/init_access.py` - заполнение исходной матрицы ролей.

## Состояния сервисов

- `running` - сервис работает;
- `maintenance` - сервис находится на обслуживании;
- `stopped` - сервис остановлен.

## Проверка

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m scripts.init_access
.\.venv\Scripts\python.exe -m scripts.verify_access --base-url http://127.0.0.1:8010
```

## Работа с проектом

Основная ветка - `main`. Изменения выполняются в тематических ветках,
проверяются тестами и объединяются через pull request. История репозитория
содержит отдельные ветки для настройки приложения и фильтрации сервисов.

> Аутентификация в лабораторной работе 19 является учебной: пароли сохраняются
> без промышленного хеширования. Такой механизм нельзя использовать в реальном
> приложении.

ЛР №20 хранит роли и разрешения, но пока не блокирует HTTP-маршруты. Проверка
разрешений для каждого запроса относится к следующей лабораторной работе.
