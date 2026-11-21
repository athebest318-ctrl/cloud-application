#!/bin/sh
# Single-container deployment; the caller must explicitly remove any previous container.
set -eu
IMAGE=${1:-cloud-application:lr37-stable}
docker run -d --name cloud-application-lr37 --restart unless-stopped \
    -p 127.0.0.1:8080:8000 \
    --env-file /etc/cloud-application/cloud-application.env \
    -e APP_HOST=0.0.0.0 -e APP_PORT=8000 -e HTTPS_ENABLED=false \
    --mount type=bind,src=/etc/cloud-application-container/secrets,dst=/app/secrets,readonly \
    "$IMAGE"
