import asyncio
import json

from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_db
from app.core.database import async_session_null_pool
from app.main import app
from app.uow import UnitOfWork


async def override_db():
    async with UnitOfWork(session_factory=async_session_null_pool) as db:
        yield db


async def main():
    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        r = await c.get("/v1/posts/offset", params={"page": 1, "page_size": 5})
        print("STATUS:", r.status_code)
        print(json.dumps(r.json(), indent=2))


asyncio.run(main())