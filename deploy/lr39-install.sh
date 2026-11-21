#!/bin/sh
# Run after LR36/LR37 on a dedicated host, with the standalone container moved off 8080.
set -eu
SOURCE=$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd)
TARGET=${1:-/opt/cloud-application/deploy}
test ! -e "$TARGET/compose.yaml"
test ! -e "$TARGET/.env"
test -r /etc/cloud-application/cloud-application.env
test -r /etc/cloud-application-container/secrets/auth_secret
install -d -m 0755 "$TARGET/docker/postgres"
install -m 0644 "$SOURCE/compose.yaml" "$TARGET/compose.yaml"
install -m 0644 "$SOURCE/docker/postgres/01_base_schema.sql" "$TARGET/docker/postgres/01_base_schema.sql"
cat > "$TARGET/.env" <<'ENV'
COMPOSE_PROJECT_NAME=cloudapp-lr38
CLOUD_APP_IMAGE=cloud-application:lr37-stable
CLOUD_ENV_FILE=/etc/cloud-application/cloud-application.env
CLOUD_SECRETS_DIR=/etc/cloud-application-container/secrets
APP_PUBLISH_IP=127.0.0.1
APP_PUBLISH_PORT=8080
ENV
cd "$TARGET"
docker compose config --quiet
docker compose up -d --wait
