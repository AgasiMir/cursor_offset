"""Производительный locustfile для честного замера ёмкости приложения.

Отличия от рабочего locustfile.py:
- Убран `wait_time` -> каждое задание выполняется сразу (максимальная пропускная способность).
- Плавный спавн через `LoadTestShape` (ramp-up -> hold -> stop).
- Чтение и запись разделены на разные классы пользователей с тегами,
  чтобы измерять их по отдельности (у них разная цена).

Запуск:
    # Читающий профиль (кэшированные GET) — основной замер ёмкости чтения
    locust -f locustfile_perf.py --host=http://localhost:8000 \
        --exclude-tags write --headless -t 5m \
        --csv=report_read --html=report_read.html

    # Пишущий профиль (create_post -> БД + инвалидация кэша)
    locust -f locustfile_perf.py --host=http://localhost:8000 \
        --exclude-tags read --headless -t 5m \
        --csv=report_write --html=report_write.html

    # Смешанный профиль (обе роли одновременно) — без флагов exclude

Параметры нагрузки задаются переменными окружения (по умолчанию в скобках):
    LOCUST_MAX_USERS  — целевое число пользователей в hold-фазе (500)
    LOCUST_RAMP_SEC   — длительность ramp-up в секундах (120)
    LOCUST_HOLD_SEC   — длительность удержания пика после ramp-up (120)

ВАЖНО: LoadTestShape переопределяет `-u` / `--spawn-rate` из CLI.
Следите за метриками сервера (CPU, RAM, Postgres, Redis) параллельно с тестом —
rps без латентности и загрузки ресурсов не говорит о "потолке".
"""

import os

from locust import HttpUser, LoadTestShape, tag, task

from app.config import get_settings

settings = get_settings()

assert settings.ENVIRONMENT == "LOCUST"


#  locust -f locustfile_perf.py --host=http://localhost:8000


# --------------------------------------------------------------------------
# Классы пользователей
# --------------------------------------------------------------------------
class ReadPostsUser(HttpUser):
    """Только кэшированные GET-запросы (fastapi-cache + Redis).

    Без `wait_time` -> Locust использует 0, т.е. запросы идут непрерывно.
    """

    @task(3)
    @tag("read")
    def get_posts_offset(self):
        self.client.get(
            "/v1/posts/offset",
            params={"page": 1, "page_size": 10},
            name="GET offset p=1 s=10",
        )

    @task(2)
    @tag("read")
    def get_posts_page20(self):
        self.client.get(
            "/v1/posts/offset",
            params={"page": 82, "page_size": 20},
            name="GET offset p=82 s=20",
        )

    @task(2)
    @tag("read")
    def get_posts_page5(self):
        self.client.get(
            "/v1/posts/offset",
            params={"page": 320, "page_size": 5},
            name="GET offset p=320 s=5",
        )

    @task(2)
    @tag("read")
    def get_post_by_uuid(self):
        self.client.get(
            "/v1/posts/8e6a526d-b2ae-4c0e-8e08-bd380b274310",
            name="GET post uuid (кэш 300s)",
        )

    @task(2)
    @tag("read")
    def get_post_by_uuid_2(self):
        self.client.get(
            "/v1/posts/99e9d8a6-0dde-464f-a716-4dd27c588434",
            name="GET post uuid (кэш 300s)",
        )


class WriteUser(HttpUser):
    """Только create_post: запись в БД + инвалидация ключа кэша."""

    @task
    @tag("write")
    def create_post(self):
        self.client.post(
            "/v1/posts/",
            json={"title": "Perf Post", "content": "Perf Content"},
            name="POST create post",
        )


# --------------------------------------------------------------------------
# Постепенный спавн: ramp-up -> hold -> stop
# --------------------------------------------------------------------------
class RampUpShape(LoadTestShape):
    target_users = int(os.getenv("LOCUST_MAX_USERS", "500"))
    ramp_sec = int(os.getenv("LOCUST_RAMP_SEC", "120"))
    hold_sec = int(os.getenv("LOCUST_HOLD_SEC", "120"))

    def tick(self):
        run_time = self.get_run_time()

        # Фаза 1: плавный набор нагрузки (линейный ramp-up)
        if run_time < self.ramp_sec:
            users = int(self.target_users * (run_time / self.ramp_sec)) + 1
            # spawn_rate подбираем так, чтобы за ramp_sec дойти до target
            spawn_rate = max(1, int(self.target_users / self.ramp_sec))
            return (users, spawn_rate)

        # Фаза 2: удержание пиковой нагрузки (здесь ищем предел сервера)
        if run_time < self.ramp_sec + self.hold_sec:
            return (self.target_users, 1)

        # Завершение теста
        return None
