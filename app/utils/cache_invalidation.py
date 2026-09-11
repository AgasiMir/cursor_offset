from uuid import UUID

from fastapi_cache import FastAPICache

from app.init import redis_manager
from app.middlewares.log import logger


async def delete_cache_key(entity_id: UUID, entity_name: str):
    """
    Удаляет ключ кэша из Redis для указанной сущности.

    Формирует полный ключ кэша, используя префикс FastAPICache,
    имя сущности и её идентификатор, затем удаляет его из Redis.

    Args:
        entity_id: UUID идентификатор сущности.
        entity_name: Имя сущности (например, 'post', 'user', 'comment').
    """
    prefix = FastAPICache.get_prefix()

    key = f"{prefix}:{entity_name}:{entity_id}"
    deleted_count = await redis_manager.delete(key)
    logger.info(f"Удален ключ кэша для сущности {entity_name} {entity_id}: {deleted_count}")
