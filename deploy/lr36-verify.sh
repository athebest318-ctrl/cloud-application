#!/bin/sh
# Controlled configuration failure on the dedicated lab installation.
set -eu
UNIT=cloud-application.service
ENV=/etc/cloud-application/cloud-application.env
BACKUP=$(mktemp /etc/cloud-application/lr36-env.XXXXXX)
cp -p "$ENV" "$BACKUP"
restore() { cp -p "$BACKUP" "$ENV"; systemctl restart "$UNIT"; rm -f "$BACKUP"; }
trap restore EXIT HUP INT TERM
ready() {
    for n in $(seq 1 30); do
        if curl -fsS http://127.0.0.1:8000/status; then printf '\n'; return 0; fi
        sleep 1
    done
    return 1
}
printf '\n=== Environment ===\n'
hostname; cat /etc/os-release; ps -p 1 -o comm=; python3 --version; git --version
id cloudapp
git -C /opt/cloud-application/app -c safe.directory=/opt/cloud-application/app log -1 --format='%H %s'
git -C /opt/cloud-application/app -c safe.directory=/opt/cloud-application/app status --short
/opt/cloud-application/venv/bin/python -m pip check
ls -ld /opt/cloud-application/app /opt/cloud-application/venv /etc/cloud-application /etc/cloud-application/secrets
ls -l "$ENV" /etc/cloud-application/secrets/* /opt/cloud-application/app/secrets
sudo -u cloudapp test -r /etc/cloud-application/secrets/auth_secret && echo AUTH_SECRET_READABLE
sudo -u cloudapp test -r /etc/cloud-application/secrets/lab_db_password && echo DB_SECRET_READABLE
printf '\n=== Configuration without secrets ===\n'
cat "$ENV"
systemctl cat "$UNIT"
systemd-analyze verify /etc/systemd/system/"$UNIT"
printf '\n=== Successful deployment ===\n'
systemctl is-enabled "$UNIT"; systemctl is-active "$UNIT"
systemctl show "$UNIT" -p MainPID -p ActiveState -p SubState -p User -p Group -p ExecMainStatus -p Restart
ps -p "$(systemctl show "$UNIT" -p MainPID --value)" -o pid,user,group,args
ss -ltnp 'sport = :8000'
ready
curl -s -o /dev/null -w 'docs HTTP %{http_code}\n' http://127.0.0.1:8000/docs
journalctl -u "$UNIT" -n 12 --no-pager
printf '\n=== Controlled APP_PORT failure ===\n'
START=$(date '+%Y-%m-%d %H:%M:%S')
sed -i 's/^APP_PORT=.*/APP_PORT=broken/' "$ENV"
systemctl restart "$UNIT"
sleep 2
systemctl show "$UNIT" -p ActiveState -p SubState -p ExecMainStatus -p Result
journalctl -u "$UNIT" --since "$START" --no-pager
systemctl stop "$UNIT"
printf '\n=== Configuration rollback ===\n'
cp -p "$BACKUP" "$ENV"
cmp -s "$BACKUP" "$ENV" && echo ENV_BACKUP_RESTORED
systemctl reset-failed "$UNIT"
systemctl start "$UNIT"
ready
systemctl is-active "$UNIT"
BEFORE=$(systemctl show "$UNIT" -p MainPID --value)
systemctl restart "$UNIT"
ready
AFTER=$(systemctl show "$UNIT" -p MainPID --value)
printf 'PID_BEFORE=%s\nPID_AFTER=%s\n' "$BEFORE" "$AFTER"
test "$BEFORE" != "$AFTER"
systemctl show "$UNIT" -p MainPID -p ActiveState -p SubState -p User -p UnitFileState
trap - EXIT HUP INT TERM
rm -f "$BACKUP"
