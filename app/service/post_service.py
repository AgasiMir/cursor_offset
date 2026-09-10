from datetime import datetime
from uuid import UUID

from app.init import redis_manager
from app.middlewares.log import logger
from app.schemas import (
    Pagination,
    PostCreateSchema,
    PostPartialUpdateSchema,
    PostReadSchema,
    PostReadSchemaWithCursor,
    PostReadSchemaWithPagination,
)
from app.uow import UnitOfWork


class PostService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_posts_with_offset(self, pagination: Pagination) -> PostReadSchemaWithPagination:
        page = pagination.page
        limit = pagination.page_size
        offset = (page - 1) * limit

        return await self.uow.posts.get_posts_with_offset(page=page, offset=offset, limit=limit)

    async def get_posts_with_cursor(
        self,
        limit: int,
        created_at: datetime | None,
        cursor_id: UUID | None,
    ) -> PostReadSchemaWithCursor:
        return await self.uow.posts.get_posts_with_cursor(
            limit=limit,
            cursor_id=cursor_id,
            created_at=created_at,
        )

    async def get_post_by_uuid(self, post_id: UUID) -> PostReadSchema:
        return await self.uow.posts.get_post(post_id)

    async def create_post(self, post: PostCreateSchema) -> PostReadSchema:
        return await self.uow.posts.create_post(post)

    async def partial_update_post(
        self, post_id: UUID, post: PostPartialUpdateSchema
    ) -> PostReadSchema:
        res = await self.uow.posts.partial_update_post(post_id=post_id, post=post)

        key = f"fastapi-cache:post:{post_id}"
        deleted_count = await redis_manager.delete(key)
        logger.info(f"Удален ключ кэша для поста {post_id}: {deleted_count}")

        return res

    async def delete_post(self, post_id: UUID) -> None:
        await self.uow.posts.delete_post(post_id)

        key = f"fastapi-cache:post:{post_id}"
        deleted_count = await redis_manager.delete(key)
        logger.info(f"Удален ключ кэша для поста {post_id}: {deleted_count}")
