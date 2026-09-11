from uuid import UUID

from fastapi_cache import FastAPICache

from app.init import redis_manager
from app.middlewares.log import logger


async def delete_cache_key(entity_id: UUID, entity_name: str):
    prefix = FastAPICache.get_prefix()

    key = f"{prefix}:{entity_name}:{entity_id}"
    deleted_count = await redis_manager.delete(key)
    logger.info(f"Удален ключ кэша для сущности {entity_id} {entity_id}: {deleted_count}")
