from locust import HttpUser, between, task

from app.config import settings

# Перед запуском нагрузочного тестирования, нужно отключить rate limiter у ручек
# locust -f locustfile.py --host=http://localhost:8000


assert settings.ENVIRONMENT == "LOCUST"


class PostsUser(HttpUser):
    wait_time = between(1, 5)  # активный период между запросами

    @task(8)
    def get_posts(self):
        self.client.get(
            "/v1/posts/offset",
            params={
                "page": 1,
                "page_size": 10,
            },
        )

    @task(8)
    def get_posts_page_size_20(self):
        self.client.get(
            "/v1/posts/offset",
            params={
                "page": 82,
                "page_size": 20,
            },
        )

    @task(8)
    def get_posts_page_2(self):
        self.client.get(
            "/v1/posts/offset",
            params={
                "page": 320,
                "page_size": 5,
            },
        )

    @task(4)
    def get_post(self):
        self.client.get(
            "/v1/posts/8e6a526d-b2ae-4c0e-8e08-bd380b274310",
        )

    @task(4)
    def get_post_2(self):
        self.client.get(
            "/v1/posts/99e9d8a6-0dde-464f-a716-4dd27c588434",
        )

    @task(2)
    def create_post(self):
        self.client.post(
            "/v1/posts/",
            json={
                "title": "Locust Post",
                "content": "Locust Content",
            },
        )

    # @task(2)
    # def get__not_existing_post(self):
    #     # Смысла особого нет, только показатель failure rate растет
    #     self.client.get(
    #         f"/v1/posts/{uuid4()}",
    #     )
