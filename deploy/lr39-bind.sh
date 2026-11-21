#!/bin/sh
# Change only the app publication in the lab Compose project.
set -eu
MODE=${1:?Usage: sh lr39-bind.sh network|loopback}
INTERFACE=${2:-eth0}
case "$MODE" in
    loopback) BIND=127.0.0.1 ;;
    network) BIND=$(ip -4 -j addr show "$INTERFACE" | python3 -c 'import sys,json; print(json.load(sys.stdin)[0]["addr_info"][0]["local"])') ;;
    *) echo 'Mode must be network or loopback' >&2; exit 2 ;;
esac
cd /opt/cloud-application/deploy
test -f .env
sed -i "s/^APP_PUBLISH_IP=.*/APP_PUBLISH_IP=$BIND/" .env
docker compose config --quiet
docker compose up -d --no-deps --force-recreate app
for n in $(seq 1 30); do
    if curl -fsS "http://$BIND:8080/status"; then printf '\n'; break; fi
    sleep 1
done
curl -fsS "http://$BIND:8080/status"
printf '\n'
docker compose port app 8000
ss -ltn 'sport = :8080'
docker compose exec -T app python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8000/status").read().decode())'
