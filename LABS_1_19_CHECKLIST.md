# Выполнение лабораторных работ 1-19

Лабораторные работы выполнены как один сквозной проект Cloud Application.
ЛР 8 сохранена в исходном виде и не создавалась повторно.

| ЛР | Тема | Реализация | Статус |
| --- | --- | --- | --- |
| 1 | Среда разработки | `.venv`, FastAPI, Uvicorn, `requirements.txt` | DONE |
| 2 | Серверное приложение | `/`, `/status`, `/about`, `/course` | DONE |
| 3 | Сетевые параметры | запуск через `run.py`, host и port в `.env` | DONE |
| 4 | HTTP-запросы | проверены методы, заголовки, коды 200, 404, 413, 422 | DONE |
| 5 | REST API | CRUD `/services` | DONE |
| 6 | Документирование API | Swagger UI, ReDoc, OpenAPI, теги и описания | DONE |
| 7 | Модульная архитектура | `routers`, `schemas`, `services`, `data` | DONE |
| 8 | Постановка задач | `PROJECT_TASKS.md`, критерии и зависимости | DONE |
| 9 | Git-репозиторий | локальный репозиторий и осмысленные коммиты | DONE |
| 10 | Ветви Git | ветвь `docs/status-description` и merge | DONE |
| 11 | Коллективная разработка | ветвь `docs/team-workflow`, подготовка к GitHub | DONE |
| 12 | Конфигурация | `pydantic-settings`, `.env`, `.env.example`, `API_PREFIX` | DONE |
| 13 | Проектирование БД | ServiceType, Service, ServiceStatusHistory | DONE |
| 14 | SQL | исходная схема и CRUD-запросы в `docs/sql` | DONE |
| 15 | SQLAlchemy | постоянное хранение сервисов в PostgreSQL | DONE |
| 16 | Alembic | baseline и последовательные миграции | DONE |
| 17 | Целостность данных | NOT NULL, UNIQUE, CHECK и Pydantic-валидация | DONE |
| 18 | Файлы и объекты | `/objects`, метаданные PostgreSQL, лимит 5 МБ | DONE |
| 19 | Аутентификация | регистрация, вход, токены, проверка и выход | DONE |

## Проверка

- `pytest`: 9 тестов пройдено.
- Интеграционный прогон: 35 HTTP-сценариев.
- Alembic: текущая версия `006_auth`.
- PostgreSQL: 7 таблиц учебного проекта.
- Перезапуск: сервисы, файлы и токены сохраняются.

Подробные результаты находятся в каталоге `evidence`.
