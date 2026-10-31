# Cloud Application

Учебное REST API для управления облачными сервисами и файлами. Данные хранятся в PostgreSQL, права доступа определяются ролями, пароли хранятся как Argon2-хеши. Реализованы задания ЛР 1–26.

## Сборка образа Docker

Запустите Docker Desktop и дождитесь запуска Engine. В PowerShell из корня проекта выполните:

```powershell
docker build -t cloud-application:0.1 .
docker image ls cloud-application
docker image inspect cloud-application:0.1
docker image history cloud-application:0.1
```

Если команда `docker` не найдена после установки Docker Desktop, откройте новое окно PowerShell либо временно добавьте путь для текущего окна:

```powershell
$env:PATH = "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin;$env:PATH"
```

Образ использует Python 3.14, непривилегированного пользователя `appuser` и метаданные порта 8000. Локальные секреты, сертификаты, настройки и данные не входят в образ. Эта работа посвящена сборке образа; для запуска контейнеру дополнительно понадобятся настройки, секреты и доступ к PostgreSQL, что рассматривается в следующей лабораторной работе. Объявление `EXPOSE` само по себе не публикует порт.

## Запуск на этом компьютере

Откройте PowerShell в папке проекта и выполните:

```powershell
.\run_windows.cmd
```

Если в `.env` установлено `HTTPS_ENABLED=true`, адрес: https://localhost:8443/docs. Локальный самоподписанный сертификат создан для обучения; браузер может попросить подтвердить исключение. Если используется доверенный `mkcert`, предупреждения не будет. При `HTTPS_ENABLED=false` адрес: http://127.0.0.1:8010/docs. Остановить сервер: `Ctrl+C`.

Сценарий демонстрации: [DEMO_GUIDE.md](DEMO_GUIDE.md). Пользователи `student01`, `student02`, `student03` имеют роли viewer, operator, administrator. Пароль учебных аккаунтов задаётся отдельно и не публикуется в Git.

## Установка на другом компьютере

1. Установите Python 3.14 и PostgreSQL, создайте базу и пользователя.
2. В папке проекта выполните:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
New-Item -ItemType Directory -Force secrets
```

3. В `.env` укажите `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`. Создайте файл `secrets/lab_db_password`, содержащий только пароль пользователя PostgreSQL. Создайте файл `secrets/auth_secret` со случайным значением. Например:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; from pathlib import Path; Path('secrets/auth_secret').write_text(secrets.token_urlsafe(32), encoding='utf-8')"
```

4. Подготовьте базу и запустите приложение:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m scripts.init_access
.\run_windows.cmd
```

Окружение PowerShell активировать не требуется. `.env`, `secrets/`, локальные сертификаты и файлы хранилища не входят в Git и архив проекта. Для HTTPS создайте сертификат `certs/localhost.pem` и ключ `certs/localhost-key.pem` с помощью `mkcert`, затем включите `HTTPS_ENABLED=true`. Без сертификата оставьте `false`.

## Проверка

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m scripts.check_secret_config
```

Ожидаемая миграция: `008_password_hash (head)`. Отмена этой миграции не восстанавливает исходные пароли: хеширование необратимо.

## Ошибки запуска

Если PowerShell запрещает `Activate.ps1`, используйте команды выше без активации. При `WinError 10013` или занятом порте измените `APP_PORT` либо `HTTPS_PORT` в `.env` или запустите `run_windows.cmd 8020`. При ошибке подключения к PostgreSQL проверьте сервер, имя БД и файл `secrets/lab_db_password`. При отсутствии сертификата создайте его или временно переключите `HTTPS_ENABLED=false`.
