from fastapi import FastAPI

from app.api import routers
from app.api.handlers import router as handlers_router
from app.handlers.errors import register_exception_handlers
from app.middlewares.log import log_requests

app = FastAPI()

app.middleware("http")(log_requests)

app.include_router(handlers_router)

for router in routers:
    app.include_router(router)

register_exception_handlers(app)
