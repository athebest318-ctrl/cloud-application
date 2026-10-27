# Зависимости Cloud Application

Среда проверки: Python 3.14, Windows. `requirements-direct.txt` содержит явно выбранные библиотеки, а `requirements.txt` фиксирует проверенные версии, включая транзитивные зависимости.

- FastAPI и Uvicorn: REST API и ASGI-сервер.
- SQLAlchemy, psycopg и Alembic: ORM, подключение PostgreSQL и миграции.
- pydantic-settings: конфигурация и секреты.
- python-multipart: загрузка файлов.
- pwdlib с Argon2: хеширование паролей.
- httpx и pytest: интеграционные и автоматические проверки.
- python-docx: работа с отчётами.

Установка: `python -m pip install -r requirements.txt`. Проверка: `python -m pip check` и `python -m pytest -q`. Новую библиотеку добавляют при необходимости, после чего проверяют совместимость, обновляют зафиксированные версии, запускают приложение и фиксируют изменения в Git. Виртуальное окружение и секреты в Git не включаются.
