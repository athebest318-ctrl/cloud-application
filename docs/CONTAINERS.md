# Контейнерный запуск Cloud Application

Образ `cloud-application:0.1` собирается командой `docker build -t cloud-application:0.1 .`. Файл `.dockerignore` исключает локальное окружение и секреты. Не добавляйте `.env` и каталог `secrets` в Git.

Для локального запуска скопируйте `.env.example` в `.env`, установите `APP_ENV=production` и создайте два текстовых файла с независимыми случайными значениями: `secrets/lab_db_password` и `secrets/auth_secret`. Значения нельзя публиковать. Затем выполните `docker compose up -d`. Приложение доступно на http://127.0.0.1:8080/docs. `docker compose down` останавливает систему, сохраняя базу в именованном томе. Не используйте `down -v`, если данные нужно сохранить.

PostgreSQL выполняет `docker/postgres/01_base_schema.sql` только при первом создании пустого тома. После проверки готовности БД сервис migrate применяет историю Alembic и инициализирует роли; затем запускается app. Приложение обращается к базе по имени сервиса `db`, а не localhost. База не публикует порт на хосте. Секреты передаются через файлы во время запуска.

Проверка: `docker compose ps -a`, `docker compose logs migrate`, `curl.exe http://127.0.0.1:8080/status` и `curl.exe http://127.0.0.1:8080/service-count`.
