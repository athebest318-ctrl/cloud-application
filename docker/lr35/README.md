# Стенд ЛР 35

Стенд предназначен для отдельного учебного контейнера с systemd, а не для установки на рабочий сервер. Он не подключает каталоги хоста. Учебный worker работает от `nobody` согласно заданию; для постоянного приложения нужна отдельная сервисная учётная запись.

Запуск из корня проекта:

```sh
docker build -t cloud-lab-systemd:lr35 docker/lr35
docker run -d --name cloud-lr35-validation --privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock --tmpfs /tmp cloud-lab-systemd:lr35
docker cp docker/lr35 cloud-lr35-validation:/root/lr35-input
docker exec cloud-lr35-validation sh /root/lr35-input/exercise.sh
```

Контейнер получает повышенные полномочия, необходимые для учебного системного менеджера. Не добавляйте к нему Docker socket и каталоги хоста. Сценарий прекращает работу при обнаружении уже существующих `/opt/cloud-lab` или unit-файла; он не предназначен для перезаписи посторонней службы.

В конце сценарий останавливает и отключает созданную службу, удаляет её конкретные файлы и пустой каталог, перечитывает конфигурацию и проверяет `LoadState=not-found`. После просмотра результатов удалите стенд:

```sh
docker stop cloud-lr35-validation
docker rm cloud-lr35-validation
```

Фактический протокол запуска находится в `evidence/labs_30_35/lr35_systemd.txt`.
