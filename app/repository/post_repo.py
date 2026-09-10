from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception_handlers.python_exceptions import PostNotFoundException
from app.models.post import Post
from app.schemas import (
    CursorReadSchema,
    Pagination,
    PostCreateSchema,
    PostPartialUpdateSchema,
    PostReadSchema,
    PostReadSchemaWithCursor,
    PostReadSchemaWithPagination,
)


class PostRepository:
    _schema: type[PostReadSchema] = PostReadSchema

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_posts_with_offset(
        self,
        page: int,
        offset: int,
        limit: int,
    ) -> PostReadSchemaWithPagination:
        posts = await self.db.scalars(
            select(Post).order_by(Post.created_at.desc()).limit(limit).offset(offset),
        )
        result = [self._schema.model_validate(post) for post in posts.all()]

        return PostReadSchemaWithPagination(
            posts=result,
            pagination=Pagination(page=page, page_size=limit),
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

        result = [self._schema.model_validate(post) for post in page_rows]

        if not result:
            return PostReadSchemaWithCursor(
                posts=[],
                has_more=False,
                next_cursor=None,
            )

        return PostReadSchemaWithCursor(
            posts=result,
            has_more=has_more,
            next_cursor=CursorReadSchema(
                last_id=result[-1].id,
                last_created_at=result[-1].created_at,
            ),
        )

    async def get_post(self, post_id: UUID) -> PostReadSchema:
        post = await self.db.get(Post, post_id)

        if not post:
            raise PostNotFoundException

        return self._schema.model_validate(post)

    async def create_post(self, post: PostCreateSchema) -> PostReadSchema:
        db_post = Post(**post.model_dump())

        self.db.add(db_post)
        await self.db.flush()

        return self._schema.model_validate(db_post)

    async def bulk_create_posts(self, posts: list[PostCreateSchema]) -> list[PostReadSchema]:
        db_posts = [Post(**post.model_dump()) for post in posts]

        self.db.add_all(db_posts)
        await self.db.flush()

        return [self._schema.model_validate(post) for post in db_posts]

    async def partial_update_post(
        self, post_id: UUID, post: PostPartialUpdateSchema
    ) -> PostReadSchema:
        db_post = await self.db.get(Post, post_id)

        if not db_post:
            raise PostNotFoundException

        for key, value in post.model_dump(exclude_unset=True).items():
            setattr(db_post, key, value)

        await self.db.flush()

        return self._schema.model_validate(db_post)

    async def delete_post(self, post_id: UUID) -> None:
        db_post = await self.db.get(Post, post_id)

        if not db_post:
            raise PostNotFoundException

        await self.db.delete(db_post)
        await self.db.flush()
