# ЛР №35. Управление службой systemd

## Цель

Проверить жизненный цикл учебной службы, работу `systemctl` и `journalctl`,
воспроизвести контролируемый отказ и восстановить службу.

Работа выполнялась в изолированном контейнере Ubuntu 24.04.5 LTS. Процессом с
PID 1 был `systemd 255`. До начала работы список `systemctl --failed` был пуст.

## Учебный процесс

Файл `/opt/cloud-lab/service_worker.py` запускает простой фоновый цикл. Каждую
секунду он записывает heartbeat в стандартный вывод. При появлении файла
`/opt/cloud-lab/fail.flag` процесс выводит понятное сообщение и завершается с
кодом 42. Это позволяет безопасно проверить диагностику отказа.

Unit-файл `/etc/systemd/system/cloud-lab-worker.service`:

```ini
[Unit]
Description=Cloud Lab background worker
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/cloud-lab
ExecStart=/usr/bin/python3 /opt/cloud-lab/service_worker.py
Restart=no
User=root

[Install]
WantedBy=multi-user.target
```

Перед загрузкой unit-файл проверен командой:

```bash
systemd-analyze verify /etc/systemd/system/cloud-lab-worker.service
systemctl daemon-reload
```

Проверка завершилась без ошибок.

## Проверка жизненного цикла

После первого запуска служба получила PID 130. После остановки и повторного
запуска PID изменился на 144, а после `restart` — на 149. Итоговые свойства:

```text
ActiveState=active
SubState=running
MainPID=149
ExecMainStatus=0
```

Команды `enable` и `disable` не заменяют запуск и остановку. В эксперименте
`enable` сделал unit включённым, но служба осталась `inactive`. После запуска
команда `disable` убрала автозапуск, однако работающий процесс остался `active`.

## Журнал и диагностика

Для проверки использовались:

```bash
journalctl -u cloud-lab-worker.service
journalctl -b -u cloud-lab-worker.service
journalctl -u cloud-lab-worker.service --since "1 minute ago"
journalctl -fu cloud-lab-worker.service
```

Контролируемый отказ воспроизведён созданием `fail.flag`. Служба перешла в
`failed`, а `systemctl show` показал `Result=exit-code` и
`ExecMainStatus=42`. В журнале зафиксировано сообщение
`fail.flag detected, exiting with code 42`.

Последовательность восстановления:

```bash
rm -f /opt/cloud-lab/fail.flag
systemctl reset-failed cloud-lab-worker.service
systemctl start cloud-lab-worker.service
systemctl is-active cloud-lab-worker.service
```

После восстановления служба вернулась в `active (running)`, код завершения
стал равен 0.

## Дополнительный эксперимент

При временной настройке `Restart=on-failure` и `RestartSec=2s` после отказа
счётчик `NRestarts` изменился с 0 на 1. systemd автоматически запустил процесс
снова, и после удаления `fail.flag` служба работала нормально. Затем настройка
возвращена к `Restart=no`.

## Очистка

После проверки служба остановлена и отключена, unit-файл и каталог
`/opt/cloud-lab` удалены, выполнены `daemon-reload` и `reset-failed`.
Заключительная команда `systemctl --failed` снова показала 0 проблемных units.

В репозитории сохранено только краткое описание команд и результатов. Полный
журнал среды и временные файлы службы не добавлялись.
