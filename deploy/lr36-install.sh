#!/bin/sh
# Run as root on a dedicated Linux learning server. Does not overwrite a deployment.
set -eu
REVISION=${1:?Usage: sh lr36-install.sh GIT_COMMIT [REPOSITORY]}
REPOSITORY=${2:-https://github.com/athebest318-ctrl/cloud-application.git}
test "$(id -u)" = 0
test ! -e /opt/cloud-application/app
test ! -e /etc/cloud-application/cloud-application.env
id cloudapp >/dev/null 2>&1 || useradd --system --user-group --home-dir /opt/cloud-application --shell /usr/sbin/nologin cloudapp
install -d -o cloudapp -g cloudapp -m 0755 /opt/cloud-application
install -d -o root -g cloudapp -m 0750 /etc/cloud-application /etc/cloud-application/secrets
sudo -u cloudapp git clone "$REPOSITORY" /opt/cloud-application/app
sudo -u cloudapp git -C /opt/cloud-application/app checkout --detach "$REVISION"
# Older revisions ignore secrets/ directories but not a symlink named secrets.
printf '\n/secrets\n' >> /opt/cloud-application/app/.git/info/exclude
sudo -u cloudapp python3 -m venv /opt/cloud-application/venv
sudo -u cloudapp /opt/cloud-application/venv/bin/python -m pip install -r /opt/cloud-application/app/requirements.txt
sudo -u cloudapp /opt/cloud-application/venv/bin/python -m pip check
sudo -u cloudapp /opt/cloud-application/venv/bin/python -c 'import fastapi, uvicorn, sqlalchemy, httpx; print("IMPORTS_OK")'
install -o root -g cloudapp -m 0640 /opt/cloud-application/app/deploy/runtime.env.example /etc/cloud-application/cloud-application.env
python3 - <<'PY'
import os, secrets, grp
for name in ('auth_secret', 'lab_db_password'):
    path = '/etc/cloud-application/secrets/' + name
    with open(path, 'x') as stream:
        stream.write(secrets.token_urlsafe(32))
    os.chown(path, 0, grp.getgrnam('cloudapp').gr_gid)
    os.chmod(path, 0o640)
PY
ln -s /etc/cloud-application/secrets /opt/cloud-application/app/secrets
install -d -o cloudapp -g cloudapp -m 0750 /opt/cloud-application/app/storage/objects
install -m 0644 /opt/cloud-application/app/deploy/cloud-application.service /etc/systemd/system/cloud-application.service
systemd-analyze verify /etc/systemd/system/cloud-application.service
systemctl daemon-reload
systemctl enable --now cloud-application.service
for n in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:8000/status; then exit 0; fi
    sleep 1
done
journalctl -u cloud-application.service -n 30 --no-pager
exit 1
