from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.api import routers
from app.api.handlers import router as handlers_router
from app.handlers.errors import register_exception_handlers
from app.init import redis_manager
from app.middlewares.log import log_requests


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await redis_manager.connect()
    assert redis_manager.redis is not None
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    try:
        yield
    finally:
        await redis_manager.close()


app = FastAPI(lifespan=lifespan, title="Cursor Offset API", version="1.0")

app.middleware("http")(log_requests)

app.include_router(handlers_router)

for router in routers:
    app.include_router(router)

register_exception_handlers(app)
