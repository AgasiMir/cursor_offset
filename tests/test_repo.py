from uuid import uuid4

import pytest

from app.exception_handlers.python_exceptions import PostNotFoundException
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
    assert len(res.model_dump()["posts"]) == 5
    assert isinstance(res, PostReadSchemaWithPagination)

    post = res.model_dump()["posts"][0]
    assert isinstance(PostReadSchema(**post), PostReadSchema)


async def test_get_posts_by_cursor(db: UnitOfWork):
    res = await db.posts.get_posts_with_cursor(4, None, None)
    assert res.model_dump()["has_more"] is True

    assert isinstance(res, PostReadSchemaWithCursor)


async def test_get_posts_by_cursor_with_no_has_more(db: UnitOfWork):
    res = await db.posts.get_posts_with_cursor(6, None, None)
    assert res.model_dump()["has_more"] is False

    assert isinstance(res, PostReadSchemaWithCursor)


async def test_get_posts_by_cursor_with_no_result(db: UnitOfWork):
    res = await db.posts.get_posts_with_cursor(5, None, None)
    last_id = res.model_dump()["posts"][-1]["id"]
    last_created_at = res.model_dump()["posts"][-1]["created_at"]

    assert res.model_dump()["next_cursor"]["last_id"] == last_id

    res = await db.posts.get_posts_with_cursor(5, last_id, last_created_at)
    assert res.model_dump()["has_more"] is False
    assert res.model_dump()["posts"] == []

    assert isinstance(res, PostReadSchemaWithCursor)


async def test_tie_break_by_cursor(db: UnitOfWork):
    page_1_res = await db.posts.get_posts_with_cursor(2, None, None)
    page_1_last_id = page_1_res.model_dump()["posts"][-1]["id"]
    page_1_last_created_at = page_1_res.model_dump()["posts"][-1]["created_at"]

    page_2_res = await db.posts.get_posts_with_cursor(2, page_1_last_id, page_1_last_created_at)
    assert page_2_res.model_dump()["posts"] != page_1_res.model_dump()["posts"]


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


async def test_post_create_with_invalid_data(db: UnitOfWork):

    with pytest.raises(TypeError):
        await db.posts.create_post(PostCreateSchema(title=None))  # type: ignore[arg-type]


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

    with pytest.raises(PostNotFoundException):
        await db.posts.get_post(post_uuid)


async def test_not_existing_post_delete(db: UnitOfWork):
    post_uuid = uuid4()

    with pytest.raises(PostNotFoundException):
        await db.posts.delete_post(post_uuid)
