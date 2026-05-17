# DevOps Practice API

Небольшое приложение для практики DevOps: **Linux + Docker + PostgreSQL + Kubernetes**.

Это приложение уже написано. Твоя задача — самостоятельно обеспечить его запуск:
написать `Dockerfile`, собрать image, запустить контейнер, подключить БД, а затем обернуть всё в Kubernetes.

> В репозитории специально **нет** `Dockerfile`, `docker-compose.yml` и Kubernetes manifest-файлов.

## Что внутри

- FastAPI HTTP API.
- PostgreSQL через SQLAlchemy.
- Alembic migrations.
- `/health/live` для liveness probe.
- `/health/ready` для readiness probe с проверкой БД.
- CRUD API для задач.
- Переменные окружения для конфигурации.
- Логи в stdout.

## Структура

```text
devops-practice-api/
├── app/
│   ├── routers/
│   │   ├── health.py
│   │   └── tasks.py
│   ├── config.py
│   ├── database.py
│   ├── logging_config.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── alembic/
│   ├── versions/
│   │   └── 0001_create_tasks_table.py
│   └── env.py
├── tests/
│   └── test_health.py
├── .env.example
├── alembic.ini
├── Makefile
└── pyproject.toml
```

## Переменные окружения

Скопируй пример:

```bash
cp .env.example .env
```

Основные переменные:

```text
APP_NAME="DevOps Practice API"
APP_ENV="local"
LOG_LEVEL="INFO"
DATABASE_URL="postgresql+psycopg://devops:devops@localhost:5432/devops_practice"
STARTUP_DELAY_SECONDS=0
FAIL_READINESS=false
```

Важно: внутри контейнера или Kubernetes `localhost` почти наверняка будет неправильным адресом БД.
Там нужно использовать имя сервиса, например `postgres`, `db` или Kubernetes Service name.

## Локальный запуск без Docker

Нужны:

- Python 3.12+
- PostgreSQL
- make, если хочешь использовать команды из `Makefile`

Установка зависимостей:

```bash
python -m venv .venv
source .venv/bin/activate

make install
```

Или без `make`:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Создай БД и пользователя PostgreSQL любым удобным способом. Пример через `psql`:

```sql
CREATE USER devops WITH PASSWORD 'devops';
CREATE DATABASE devops_practice OWNER devops;
```

Примени миграции:

```bash
alembic upgrade head
```

Запусти приложение:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Проверка:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

## API examples

Создать задачу:

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Write Dockerfile","description":"Containerize the API"}'
```

Получить список задач:

```bash
curl http://localhost:8000/tasks
```

Получить задачу по ID:

```bash
curl http://localhost:8000/tasks/1
```

Обновить задачу:

```bash
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'
```

Удалить задачу:

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

## Что нужно сделать самостоятельно

### 1. Dockerfile

Напиши `Dockerfile`, который:

- использует Python 3.12;
- устанавливает зависимости;
- копирует приложение;
- запускает приложение через `uvicorn`;
- слушает `0.0.0.0:8000`;
- не запускает приложение от root-пользователя;
- не содержит секретов внутри image.

Минимальная проверка после сборки:

```bash
docker build -t devops-practice-api .
docker run --rm -p 8000:8000 devops-practice-api
curl http://localhost:8000/health/live
```

На этом этапе `/health/ready` может падать, если контейнер не видит PostgreSQL. Это нормально.

### 2. Контейнер + PostgreSQL

Обеспечь работу приложения с PostgreSQL.

Тебе нужно решить:

- как запустить PostgreSQL;
- как создать пользователя и БД;
- как передать `DATABASE_URL` в приложение;
- как сохранить данные PostgreSQL между перезапусками;
- как выполнить `alembic upgrade head`;
- как посмотреть логи приложения;
- как зайти внутрь контейнера и проверить сеть.

Команды, которые пригодятся:

```bash
docker logs
docker exec -it
docker network ls
docker network inspect
docker volume ls
docker volume inspect
```

### 3. Kubernetes

Оберни приложение в Kubernetes.

Минимум, который стоит сделать:

- `Namespace`;
- `ConfigMap` для обычных настроек;
- `Secret` для строки подключения к БД или пароля;
- `Deployment` для приложения;
- `Service` для приложения;
- `readinessProbe` на `/health/ready`;
- `livenessProbe` на `/health/live`;
- отдельный PostgreSQL или подключение к внешней БД.

Дополнительный плюс:

- `initContainer` или `Job` для миграций;
- `resources.requests` и `resources.limits`;
- `securityContext`;
- запуск от non-root user;
- `Ingress`;
- `HorizontalPodAutoscaler`.

## Поведение health endpoints

### Liveness

```bash
curl http://localhost:8000/health/live
```

Не проверяет БД. Используется, чтобы понять, жив ли процесс.

### Readiness

```bash
curl http://localhost:8000/health/ready
```

Проверяет подключение к БД. Если PostgreSQL недоступен, endpoint вернёт `503`.

Это удобно для Kubernetes `readinessProbe`: Pod не должен получать трафик, пока приложение не может работать с БД.

## Полезные сценарии для тренировки

### Сломать readiness вручную

Запусти приложение с переменной:

```bash
FAIL_READINESS=true
```

Теперь `/health/ready` будет возвращать `503`.

### Замедлить старт приложения

Запусти приложение с переменной:

```bash
STARTUP_DELAY_SECONDS=15
```

Это удобно для практики `startupProbe` или настройки probe delays в Kubernetes.

## Критерии готовности

Ты хорошо подготовился, если можешь:

- собрать Docker image;
- запустить приложение в контейнере;
- передать env-переменные в контейнер;
- подключить контейнер к PostgreSQL;
- выполнить миграции;
- объяснить, почему `localhost` внутри контейнера не равен твоему хосту;
- посмотреть логи;
- зайти внутрь контейнера;
- задеплоить приложение в Kubernetes;
- настроить `readinessProbe` и `livenessProbe`;
- объяснить разницу между `Deployment`, `Service`, `ConfigMap`, `Secret`;
- объяснить, где хранятся данные PostgreSQL.

## Подсказка без готового решения

Для production-подхода лучше не хранить пароль БД в открытом YAML-файле.
Используй Secret или внешний secret manager.

Миграции можно запускать:

- вручную перед стартом приложения;
- отдельным Kubernetes Job;
- initContainer;
- entrypoint-скриптом.

Для стажировки достаточно уметь объяснить плюсы и минусы каждого подхода.
