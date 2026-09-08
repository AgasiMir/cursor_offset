from uuid import uuid4

import pytest

from app.exceptions.python_exceptions import PostNotFoundException
from app.schemas import (
    PostCreateSchema,
    PostPartialUpdateSchema,
    PostReadSchema,
    PostReadSchemaWithCursor,
    PostReadSchemaWithPagination,
)
from app.uow import UnitOfWork


async def test_get_posts_by_offset(db: UnitOfWork):
    res = await db.posts.get_posts_with_offset(1, 0, 5)
    assert len(res.model_dump()["posts"]) == res.model_dump()["posts_on_page"] == 5
    assert isinstance(res, PostReadSchemaWithPagination)

    post = res.model_dump()["posts"][0]
    assert isinstance(PostReadSchema(**post), PostReadSchema)


async def test_get_posts_by_cursor(db: UnitOfWork):
    res = await db.posts.get_posts_with_cursor(4)
    assert res.model_dump()["has_more"] is True

    assert isinstance(res, PostReadSchemaWithCursor)


async def test_get_posts_by_cursor_with_no_has_more(db: UnitOfWork):
    res = await db.posts.get_posts_with_cursor(6)
    assert res.model_dump()["has_more"] is False

    assert isinstance(res, PostReadSchemaWithCursor)


async def test_get_posts_by_cursor_with_no_result(db: UnitOfWork):
    res = await db.posts.get_posts_with_cursor(0)
    assert res.model_dump()["next_cursor"] is None

    assert isinstance(res, PostReadSchemaWithCursor)


async def test_get_post_by_uuid(db: UnitOfWork):
    paginated = await db.posts.get_posts_with_offset(1, 0, 5)
    post_uuid = paginated.model_dump()["posts"][0]["id"]

    post = await db.posts.get_post(post_uuid)
    assert post.model_dump()["id"] == post_uuid

    assert isinstance(post, PostReadSchema)


async def test_get_not_existingpost_by_uuid(db: UnitOfWork):
    post_uuid = uuid4()

    with pytest.raises(PostNotFoundException):
        await db.posts.get_post(post_uuid)


async def test_post_create(db: UnitOfWork):
    post_data = PostCreateSchema(title="test", content="test")

    res = await db.posts.create_post(post_data)
    assert isinstance(res, PostReadSchema)


async def test_post_partial_update(db: UnitOfWork):
    paginated = await db.posts.get_posts_with_offset(1, 0, 5)
    post_uuid = paginated.model_dump()["posts"][0]["id"]

    post = await db.posts.get_post(post_uuid)
    updated_post = PostPartialUpdateSchema(title="test_updated")

    res = await db.posts.partial_update_post(post.id, updated_post)
    assert res.model_dump()["title"] == "test_updated"

    assert isinstance(res, PostReadSchema)


async def test_not_existingpost_partial_update(db: UnitOfWork):

    post_uuid = uuid4()
    updated_post = PostPartialUpdateSchema(title="test_updated")
    with pytest.raises(PostNotFoundException):
        await db.posts.partial_update_post(post_uuid, updated_post)


async def test_post_delete(db: UnitOfWork):
    paginated = await db.posts.get_posts_with_offset(1, 0, 5)
    post_uuid = paginated.model_dump()["posts"][0]["id"]

    await db.posts.delete_post(post_uuid)


async def test_not_existing_post_delete(db: UnitOfWork):
    post_uuid = uuid4()

    with pytest.raises(PostNotFoundException):
        await db.posts.delete_post(post_uuid)
