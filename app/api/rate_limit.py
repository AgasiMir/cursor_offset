from fastapi.routing import iter_route_contexts
from fastapi_limiter.depends import RateLimiter as BaseRateLimiter
from starlette.requests import Request
from starlette.responses import Response


class RateLimiter(BaseRateLimiter):
    """Rate limiter, совместимый с новыми версиями FastAPI.

    Начиная с FastAPI 0.121+ метод ``include_router`` больше не раскладывает
    вложенные роутеры в плоский список :class:`APIRoute`: вместо этого в
    ``app.routes`` помещается обёртка ``_IncludedRouter``, у которой нет
    атрибута ``path``. Базовый ``fastapi_limiter.RateLimiter`` напрямую
    обращается к ``route.path`` и падает с ``AttributeError``.

    Здесь перебор маршрутов выполняется через
    :func:`fastapi.routing.iter_route_contexts`, который рекурсивно раскрывает
    вложенные роутеры и выдаёт полные пути (с учётом префиксов).
    """

    async def __call__(self, request: Request, response: Response):
        route_index = 0
        dep_index = 0
        for i, route in enumerate(iter_route_contexts(request.app.routes)):
            if (
                route.path == request.scope["path"]
                and route.methods
                and request.method in route.methods
            ):
                route_index = i
                endpoint = getattr(route, "endpoint", None)
                if endpoint is not None and getattr(endpoint, "_skip_limiter", False):
                    return
                for j, dependency in enumerate(route.dependencies):
                    if self is dependency.dependency:
                        dep_index = j
                        break

        rate_key = await self.identifier(request)
        key = f"{rate_key}:{route_index}:{dep_index}"
        success = await self.limiter.try_acquire_async(key, blocking=self.blocking)
        if not success:
            return await self.callback(request, response)
