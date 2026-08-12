# Django-REST-Framework-Homework
Репозиторий для решения домашней работы по Django-REST-Framework

## Запуск через Docker

1. Скопируйте файл `.env.example` в `.env` и заполните переменные.
2. Соберите и запустите сервисы:
   - `docker compose up --build`
3. Выполните миграции внутри контейнера Django.
4. При необходимости создайте суперпользователя.

## Сервисы

- `web` — Django-приложение
- `db` — PostgreSQL
- `redis` — брокер и кэш для Celery
- `celery-worker` — выполнение фоновых задач
- `celery-beat` — периодические задачи
