#!/bin/sh
set -eu
IMAGE=cloud-application:lr37-stable
NAME=cloud-application-lr37
ROOT=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
ready() {
    for n in $(seq 1 30); do
        if curl -fsS http://127.0.0.1:8080/status; then printf '\n'; return 0; fi
        sleep 1
    done
    return 1
}
printf '\n=== Image and daemon ===\n'
systemctl is-active docker
docker version --format 'Client={{.Client.Version}} Server={{.Server.Version}}'
docker image inspect "$IMAGE" --format 'ID={{.Id}} Revision={{index .Config.Labels "org.opencontainers.image.revision"}} User={{.Config.User}}'
UID_APP=$(docker run --rm --entrypoint id "$IMAGE" -u appuser)
GID_APP=$(docker run --rm --entrypoint id "$IMAGE" -g appuser)
printf 'APP_UID=%s APP_GID=%s\n' "$UID_APP" "$GID_APP"
install -d -o "$UID_APP" -g "$GID_APP" -m 0750 /etc/cloud-application-container/secrets
for secret in auth_secret lab_db_password; do
    install -o "$UID_APP" -g "$GID_APP" -m 0640 /etc/cloud-application/secrets/"$secret" /etc/cloud-application-container/secrets/"$secret"
done
ls -ldn /etc/cloud-application-container/secrets
ls -ln /etc/cloud-application-container/secrets/*
sh "$ROOT/lr37-run.sh" "$IMAGE"
ready
curl -s -o /dev/null -w 'docs HTTP %{http_code}\n' http://127.0.0.1:8080/docs
docker ps --filter name="$NAME"
docker port "$NAME"
docker inspect "$NAME" --format 'Image={{.Image}} Tag={{.Config.Image}} Restart={{.HostConfig.RestartPolicy.Name}} State={{.State.Status}} PID={{.State.Pid}} Mounts={{json .Mounts}}'
docker exec "$NAME" whoami
docker exec "$NAME" pwd
docker exec "$NAME" python --version
docker exec "$NAME" sh -c 'test -r /app/secrets/auth_secret && echo AUTH_SECRET_READABLE; test -r /app/secrets/lab_db_password && echo DB_SECRET_READABLE'
docker logs --tail 12 "$NAME"
timeout 2 docker logs -f --tail 0 "$NAME" || test "$?" = 124
printf '\n=== Lifecycle ===\n'
docker stop "$NAME"
docker ps -a --filter name="$NAME"
docker start "$NAME"
ready
BEFORE=$(docker inspect "$NAME" --format '{{.State.Pid}}')
docker restart "$NAME"
ready
AFTER=$(docker inspect "$NAME" --format '{{.State.Pid}}')
printf 'PID_BEFORE=%s\nPID_AFTER=%s\n' "$BEFORE" "$AFTER"
test "$BEFORE" != "$AFTER"
printf '\n=== Failed release ===\n'
BAD_DIR=$(mktemp -d /tmp/lr37-bad.XXXXXX)
printf 'FROM cloud-application:lr37-stable\nCMD ["python", "/app/missing-release.py"]\n' > "$BAD_DIR/Dockerfile"
cat "$BAD_DIR/Dockerfile"
docker build -t cloud-application:lr37-bad "$BAD_DIR"
docker stop "$NAME"
docker rm "$NAME"
docker run -d --name "$NAME" --restart no cloud-application:lr37-bad
sleep 2
docker ps -a --filter name="$NAME"
docker inspect "$NAME" --format 'Tag={{.Config.Image}} State={{.State.Status}} ExitCode={{.State.ExitCode}}'
docker logs "$NAME" 2>&1
test "$(docker inspect "$NAME" --format '{{.State.ExitCode}}')" = 2
printf '\n=== Image rollback ===\n'
docker rm "$NAME"
sh "$ROOT/lr37-run.sh" "$IMAGE"
ready
docker inspect "$NAME" --format 'Image={{.Image}} Tag={{.Config.Image}} Restart={{.HostConfig.RestartPolicy.Name}} State={{.State.Status}} PID={{.State.Pid}} Mounts={{json .Mounts}}'
curl -s -o /dev/null -w 'docs HTTP %{http_code}\n' http://127.0.0.1:8080/docs
printf '\n=== Docker daemon restart ===\n'
systemctl restart docker
ready
docker ps --filter name="$NAME"
docker image rm cloud-application:lr37-bad
rm "$BAD_DIR/Dockerfile"
rmdir "$BAD_DIR"
