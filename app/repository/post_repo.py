from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.python_exceptions import PostNotFoundException
from app.models.post import Post
from app.schemas import (
    Cursor,
    PostCreateSchema,
    PostPartialUpdateSchema,
    PostReadSchema,
    PostReadSchemaWithCursor,
    PostReadSchemaWithPagination,
)
from app.utils.pagination import Pagination


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    async def _model_to_schema(model: Post) -> PostReadSchema:
        return PostReadSchema.model_validate(model)

    async def get_posts_with_offset(self, offset: int, limit: int) -> PostReadSchemaWithPagination:
        posts = await self.db.scalars(
            select(Post).order_by(Post.created_at.desc()).limit(limit).offset(offset),
        )
        result = [await self._model_to_schema(post) for post in posts.all()]

        return PostReadSchemaWithPagination(
            posts=result,
            posts_on_page=len(result),
            pagination=Pagination(page=offset + 1, page_size=limit),
        )

    async def get_posts_with_cursor(
        self,
        limit: int,
        cursor_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> PostReadSchemaWithCursor:
        # запрашиваем на одну запись больше, чтобы понять, есть ли следующая страница
        stmt = select(Post).order_by(Post.created_at.desc(), Post.id.desc()).limit(limit + 1)

        # следующая страница = записи "старше" курсора (порядок DESC);
        # при отсутствии курсора — первая страница без WHERE
        if cursor_id is not None and created_at is not None:
            stmt = stmt.where(
                or_(
                    Post.created_at < created_at,
                    and_(
                        Post.created_at == created_at,
                        Post.id < cursor_id,
                    ),
                )
            )

        rows = list((await self.db.scalars(stmt)).all())

        has_more = len(rows) > limit  # есть ли запись за пределами страницы
        page_rows = rows[:limit]  # отрезаем лишнюю "смотрящую" запись

        result = [await self._model_to_schema(post) for post in page_rows]

        if not result:
            return PostReadSchemaWithCursor(posts=[], has_more=False, next_cursor=None)

        return PostReadSchemaWithCursor(
            posts=result,
            has_more=has_more,
            next_cursor=Cursor(
                id=result[-1].id,
                created_at=result[-1].created_at,
            ),
        )

    async def get_post(self, post_id: UUID) -> PostReadSchema:
        post = await self.db.get(Post, post_id)

        if not post:
            raise PostNotFoundException

        return await self._model_to_schema(post)

    async def create_post(self, post: PostCreateSchema) -> PostReadSchema:
        db_post = Post(**post.model_dump())

        self.db.add(db_post)
        await self.db.flush()

        return await self._model_to_schema(db_post)

    async def bulk_create_posts(self, posts: list[dict[str, str]]) -> list[PostReadSchema]:
        db_posts = [Post(**post) for post in posts]

        self.db.add_all(db_posts)
        await self.db.flush()

        return [await self._model_to_schema(post) for post in db_posts]

    async def partial_update_post(
        self, post_id: UUID, post: PostPartialUpdateSchema
    ) -> PostReadSchema:
        db_post = await self.db.get(Post, post_id)

        if not db_post:
            raise PostNotFoundException

        for key, value in post.model_dump(exclude_unset=True).items():
            setattr(db_post, key, value)

        await self.db.flush()

        return await self._model_to_schema(db_post)

    async def delete_post(self, post_id: UUID) -> dict:
        db_post = await self.db.get(Post, post_id)

        if not db_post:
            raise PostNotFoundException

        await self.db.delete(db_post)

        return {"message": "Post deleted."}
