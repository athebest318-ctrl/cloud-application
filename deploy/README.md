# Локальное развёртывание

Сценарии рассчитаны на отдельную Linux-среду с systemd, Git, Python 3.12+, venv, curl и Docker Engine с Compose v2. Секреты создаются на сервере и не входят в Git.

ЛР 36: `sudo sh deploy/lr36-install.sh COMMIT` получает конкретную ревизию и создаёт venv, конфигурацию, секреты и systemd-службу. Существующая установка не перезаписывается. Проверки: `systemctl is-active cloud-application`, `curl -f http://127.0.0.1:8000/status`, `journalctl -u cloud-application`. Перед экспериментом с APP_PORT сохраните env-файл, после диагностики верните его и перезапустите службу. Менять unit или делать daemon-reload для изменения только env-файла не требуется.

ЛР 37: соберите `docker build --build-arg GIT_REVISION=$(git rev-parse HEAD) -t cloud-application:lr37-stable .`. В `/etc/cloud-application-container/secrets` скопируйте секреты из ЛР 36, установите владельца по фактическим UID/GID appuser в образе, права каталогов 0750 и файлов 0640. Запуск: `sudo sh deploy/lr37-run.sh`. Mount доступен только для чтения; порт опубликован на loopback. Для rollback сохраните стабильный Image ID, исследуйте logs и ExitCode неудачного контейнера, удалите только этот контейнер и повторите стабильный запуск.

ЛР 39: `sudo sh deploy/lr39-install.sh` создаёт отдельный каталог `/opt/cloud-application/deploy`, копирует `compose.yaml` вместе с `docker/postgres/*.sql`, создаёт Compose `.env` и поднимает систему. Копирование SQL обязательно: первая миграция предполагает наличие исходных таблиц ЛР 14. Для существующего deployment сценарий останавливается до изменений. `CLOUD_ENV_FILE` содержит обычные настройки runtime, а `CLOUD_SECRETS_DIR` указывает на внешний каталог секретов. Задайте фактический IP Linux-интерфейса. По умолчанию публикация остаётся локальной.

```dotenv
COMPOSE_PROJECT_NAME=cloudapp-lr38
CLOUD_APP_IMAGE=cloud-application:lr37-stable
CLOUD_ENV_FILE=/etc/cloud-application/cloud-application.env
CLOUD_SECRETS_DIR=/etc/cloud-application-container/secrets
APP_PUBLISH_IP=127.0.0.1
APP_PUBLISH_PORT=8080
```

Проверка: `docker compose config --quiet`, затем `docker compose up -d --wait`. PostgreSQL и Notification Service не имеют опубликованных портов. Миграции выполняются отдельным одноразовым сервисом. Для изменения адреса отредактируйте APP_PUBLISH_IP и выполните `docker compose up -d --no-deps --force-recreate app`; простой restart не применяет новую публикацию. Проверяйте `/status`, `/docs` и закрытые порты 5432/9000 с Windows. При диагностическом возврате на loopback внутренний `/status` должен работать, а запрос с Windows на сетевой IP — завершаться отказом. После эксперимента восстановите сетевой IP.

Среда WSL 2 использует виртуальную NAT-сеть Hyper-V, а не два адаптера VirtualBox. В таком варианте адрес Windows берётся из vEthernet WSL, адрес Linux — из `ip -br addr`. Не используйте IP физической сети и не меняйте firewall. После перезапуска WSL адрес может измениться: обновите APP_PUBLISH_IP и пересоздайте только app.
