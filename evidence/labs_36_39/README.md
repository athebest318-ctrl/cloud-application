# Протоколы ЛР 36 37 и 39

Дата выполнения: 21 ноября 2026 года. Автор отчётов: Дьяченко Артем.

Среда — отдельная Ubuntu WSL 2 CloudLabs на локальном Windows-компьютере. Приложение из Git commit `673e97690b557a5b2e8131d7677407e24108cdf8`. Image `cloud-application:lr37-stable`, revision label совпадает с commit. Итоговые исправления эксплуатационных сценариев и отчёты добавлены последующим коммитом; runtime-код приложения не изменён.

- `lr36-install.txt`, `lr36-verify.txt`: установка systemd-приложения, venv, права, успешный запуск, ошибка APP_PORT, диагностика, rollback и смена PID. В первом протоколе `git status` видна ссылка secrets до добавления локального исключения; в итоговом snapshot статус чистый.
- `lr37-build.txt`, `lr37-verify.txt`: сборка, UID/GID, read-only mount, lifecycle, неработающий image, ExitCode 2, восстановление прежнего image и перезапуск Docker daemon.
- `lr39-prepare.txt`, `lr39-recovery.txt`: первый запуск Compose и восстановление после отсутствия относительного SQL-каталога в deployment. Содержимое внешней конфигурации и секретов не выводится.
- `lr39-clean-deploy.txt`: проверка исправленного установщика с новым Compose-проектом и чистым PostgreSQL volume; миграция достигает `008_password_hash`. После проверки временные контейнеры и сеть остановлены и удалены, volumes сохранены.
- `lr39-before.txt`, `lr39-network.txt`, `lr39-controlled-failure.txt`: публикация, ss и внутренний HTTP при переключении bind.
- `lr39-windows-*.json`: реальные проверки Windows TCP/HTTP на сетевой IPv4 Linux; отрицательный тест loopback, положительный сетевой тест и контролируемый отказ.
- `lr39-runtime.json`: 18 проверок API, включая доступ к БД, объектное хранилище, Notification Service, разграничение доступа и сохранность данных после restart app. Тестовые сервис, файл, сессия и пользователь удалены после проверки; секреты и session token не сохраняются.
- `restart-wsl.txt`: повторная загрузка только дистрибутива CloudLabs, автозапуск systemd-службы и контейнеров, успешный HTTP.
- `snapshot.json`: выборочный паспорт среды без значений секретов и полного container environment.
- `pytest.txt`, `quality.txt`, `final-checks.json`: тесты, Ruff, синтаксис shell, доступность HTTP, проверка секретов и структура Word-отчётов.
- `lr39-swagger.jpg`: реальный снимок страницы Swagger UI, открытой в Microsoft Edge Windows по сетевому IP Linux. Остальные figure PNG — поясняющие схемы, а не снимки интерфейса.

Сценарии воспроизведения размещены в `deploy/`. WSL 2 NAT заменяет учебную топологию VirtualBox с двумя адаптерами; отдельная VirtualBox Host-only сеть не создавалась. Сетевые IP действительны на момент проверки и могут измениться после полной перезагрузки WSL. Правила firewall не менялись. В образе минимальной Ubuntu имеется отдельный failed unit kmod-static-nodes; systemd-служба приложения и Docker находятся в active.
