from app.config import get_settings
from app.connectors.redis_connector import RedisManager

settings = get_settings()

redis_manager = RedisManager(port=settings.REDIS_PORT, host=settings.REDIS_HOST)
