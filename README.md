# Lantern

Статичний сервіс Nginx повертає головну сторінку, JSON зі станом і HTTP 404 для відсутнього ресурсу. Версія застосунку — `devops6-lantern-73`. Docker Compose публікує порт контейнера 8000 на локальному порту 8592.

## Встановлення та запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export BASE_URL=http://127.0.0.1:8592
export EXPECTED_RELEASE=devops6-lantern-73
export CHECK_TIMEOUT=2.5
docker compose build
docker compose up -d --no-build --wait --wait-timeout 15
curl --fail --max-time 5 "$BASE_URL/"
```

## Перевірка

```bash
python -m pytest -v --hosts=docker://lantern-web tests
python verify_lantern.py
```

Справний варіант проходить 16 тестів. Testinfra працює з файлами й конфігурацією усередині контейнера. HTTPX перевіряє відповіді через опублікований порт. Команда verify_lantern працює через curl і повертає 0, 1 або 2 для успіху, помилки або тайм-ауту.

## Досліди та відновлення

Перед кожним сценарієм перевір справне середовище. Виконуй команди по одній. Після зміни та після відновлення повтори pytest і verify_lantern.

1. Помилкове відображення порту.

   ```bash
   LANTERN_PORT=8593 docker compose up -d --no-build --force-recreate --wait --wait-timeout 15
   docker compose port web 8000
   curl --fail --max-time 5 http://127.0.0.1:8593/
   ```

   Для відновлення виконай ту саму команду Compose зі значенням `LANTERN_PORT=8592`. Для перевірок використовуй початковий `BASE_URL` 8592.

2. Застарілі метадані.

   ```bash
   docker exec lantern-web sh -c 'printf "%s\n" "{\"status\":\"available\",\"release\":\"devops6-lantern-72\"}" > /usr/share/lantern/health.json'
   curl --fail --max-time 5 "$BASE_URL/health.json"
   ```

   Поверни початкові метадані командою `docker cp site/health.json lantern-web:/usr/share/lantern/health.json`.

3. Пауза контейнера. Виконай `docker pause lantern-web`, проганяй перевірки, потім виконай `docker unpause lantern-web` й перевір повторно.

Видали навчальне середовище командою `docker compose down`. Для повторного відтворення виконай команди з розділу запуску.

## GitHub Actions

Workflow `.github/workflows/compose-check.yml` запускається після push тегів `lab-*`. У гілці `lantern-health-check` підготуй коміт із застарілим значенням `release` у `site/health.json`. Познач його тегом `lab-stale-metadata` й відправ цей тег. Другим комітом поверни очікуваний ідентифікатор і відправ тег `lab-restored-metadata`. У підсумку кожного запуску є статуси груп перевірок, а в артефакті `lantern-compose-evidence` — XML, вихід команди й логи Nginx. CI видаляє контейнер і мережу Compose.

## Базове демо

```bash
docker build -t devops6-demo ./demo
docker run -d --name devops6-web -p 127.0.0.1:8080:80 devops6-demo
curl --fail --max-time 5 http://127.0.0.1:8080/
python -m pytest -v --hosts=docker://devops6-web demo/tests/infra
docker rm -f devops6-web
```
