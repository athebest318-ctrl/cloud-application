# Проверка зависимостей

- Python 3.14, Windows; проверочное окружение `.venv-check` создано отдельно.
- Установка `requirements.txt` в чистое окружение завершилась успешно.
- `pip check`: `No broken requirements found`.
- `pytest`: 20 проверок прошли, 2 предупреждения об устаревающих интерфейсах зависимостей.
- FastAPI 0.141.1 требует annotated-doc, pydantic, starlette, typing-extensions и typing-inspection. Используется в `app/main.py` и маршрутизаторах; без него REST API не запускается.
- После удаления `python-multipart` в `.venv-check` команда `pip check` не показала конфликта, но импорт `app.main` завершился ошибкой `Form data requires python-multipart`. Пакет версии 0.0.32 восстановлен.
- При анализе обновлений обнаружены, например, Alembic 1.20.1, FastAPI 0.162.0 и SQLAlchemy 2.1.6. Массовое обновление не выполнялось.
