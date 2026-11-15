set -eu
unit=cloud-lab-worker.service
[ "$(ps -p 1 -o comm=)" = systemd ]
[ ! -e /opt/cloud-lab ]
[ ! -e /etc/systemd/system/$unit ]
mkdir -m 0755 /opt/cloud-lab
cp /root/lr35-input/service_worker.py /opt/cloud-lab/service_worker.py
cp /root/lr35-input/cloud-lab-worker.service /etc/systemd/system/$unit
chmod 0644 /opt/cloud-lab/service_worker.py /etc/systemd/system/$unit
printf '\nENVIRONMENT\n'
whoami
cat /etc/os-release
hostnamectl
systemctl --version | head -1
systemctl --failed --no-pager
systemctl list-units --type=service --state=running --no-pager
systemd-analyze verify /etc/systemd/system/$unit
systemctl daemon-reload
printf '\nBEFORE_START\n'
systemctl show "$unit" -p ActiveState -p SubState -p UnitFileState
systemctl start "$unit"
sleep 1
printf '\nAFTER_START\n'
systemctl show "$unit" -p ActiveState -p SubState -p MainPID -p ExecMainStatus -p UnitFileState
pid=$(systemctl show "$unit" -p MainPID --value)
ps -fp "$pid"
systemctl stop "$unit"
printf '\nAFTER_STOP\n'
systemctl show "$unit" -p ActiveState -p MainPID
systemctl enable "$unit"
printf '\nENABLE_WITHOUT_START\n'
systemctl show "$unit" -p ActiveState -p UnitFileState
systemctl start "$unit"
pid2=$(systemctl show "$unit" -p MainPID --value)
systemctl restart "$unit"
pid3=$(systemctl show "$unit" -p MainPID --value)
printf 'RESTART_PID_BEFORE=%s AFTER=%s\n' "$pid2" "$pid3"
[ "$pid2" != "$pid3" ]
systemctl disable "$unit"
printf '\nDISABLE_WITHOUT_STOP\n'
systemctl show "$unit" -p ActiveState -p UnitFileState
printf '\nJOURNAL_CURRENT_BOOT\n'
journalctl -u "$unit" -b --no-pager -n 15
printf '\nJOURNAL_TIME_FILTER\n'
journalctl -u "$unit" --since '5 minutes ago' --no-pager -n 10
printf '\nJOURNAL_FOLLOW\n'
timeout 6 journalctl -u "$unit" -f -n 0 --no-pager || [ "$?" = 124 ]
systemctl stop "$unit"
touch /opt/cloud-lab/fail.flag
systemctl start "$unit" || true
sleep 1
printf '\nCONTROLLED_FAILURE\n'
systemctl show "$unit" -p ActiveState -p SubState -p ExecMainStatus -p Result
[ "$(systemctl show "$unit" -p ExecMainStatus --value)" = 42 ]
systemctl --failed --no-pager
journalctl -u "$unit" --no-pager -n 8
rm /opt/cloud-lab/fail.flag
systemctl reset-failed "$unit"
systemctl start "$unit"
sleep 1
printf '\nRECOVERED_PROPERTIES\n'
systemctl show "$unit" -p Description -p LoadState -p ActiveState -p SubState -p UnitFileState -p User -p WorkingDirectory -p ExecStart -p MainPID -p ExecMainStatus
systemctl stop "$unit"
sed -i 's/Restart=no/Restart=on-failure\nRestartSec=2/' /etc/systemd/system/$unit
systemctl daemon-reload
touch /opt/cloud-lab/fail.flag
systemctl start "$unit"
sleep 3
printf '\nAUTOMATIC_RESTART\n'
systemctl show "$unit" -p NRestarts -p ActiveState -p SubState
rm /opt/cloud-lab/fail.flag
sleep 3
systemctl is-active "$unit"
systemctl stop "$unit"
sed -i '/RestartSec=2/d;s/Restart=on-failure/Restart=no/' /etc/systemd/system/$unit
systemctl daemon-reload
systemctl reset-failed "$unit" 2>/dev/null || true
systemctl start "$unit"
systemctl is-active "$unit"
printf '\nCLEANUP\n'
systemctl disable --now "$unit"
rm /etc/systemd/system/$unit
rm /opt/cloud-lab/service_worker.py
rmdir /opt/cloud-lab
systemctl daemon-reload
systemctl reset-failed "$unit" 2>/dev/null || true
systemctl show "$unit" -p LoadState
systemctl --failed --no-pager
