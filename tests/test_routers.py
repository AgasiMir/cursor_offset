from uuid import uuid4

from app.schemas import PostReadSchema, PostReadSchemaWithCursor, PostReadSchemaWithPagination
from app.uow import UnitOfWork


async def test_get_posts_by_offset(async_client):
    titles = []
    res = await async_client.get(
        "/v1/posts/offset",
        params={"page": 1, "page_size": 5},
    )
    assert res.status_code == 200

    for post in res.json().get("posts"):
        titles.append(post["title"])
    assert "And the last but not least, the 5th test post" in titles


async def test_get_posts_by_offset_with_no_posts(async_client):
    res = await async_client.get(
        "/v1/posts/offset",
        params={"page": 2, "page_size": 5},
    )
    assert res.status_code == 200
    assert res.json().get("posts") == []
    assert isinstance(PostReadSchemaWithPagination(**res.json()), PostReadSchemaWithPagination)


async def test_get_posts_by_cursor(async_client):
    res = await async_client.get(
        "/v1/posts/cursor",
        params={"page": 1, "page_size": 4},
    )
    assert res.status_code == 200
    assert res.json().get("has_more") is True
    assert isinstance(PostReadSchemaWithCursor(**res.json()), PostReadSchemaWithCursor)


async def test_get_posts_by_cursor_with_has_more_is_false(async_client):
    res = await async_client.get(
        "/v1/posts/cursor",
        params={"page": 1, "page_size": 5},
    )
    assert res.status_code == 200
    assert res.json().get("has_more") is False


async def test_get_post_by_uuid(async_client, db: UnitOfWork):
    paginated = await db.posts.get_posts_with_offset(0, 5)
    post_id = paginated.model_dump()["posts"][0]["id"]

    res = await async_client.get(
        f"/v1/posts/{post_id}",
    )
    assert res.status_code == 200


async def test_get_not_existing_post_by_uuid(async_client):
    post_id = uuid4()

    res = await async_client.get(
        f"/v1/posts/{post_id}",
    )
    assert res.status_code == 404
    assert res.json().get("message") == "Post Not Found."


async def test_create_post(async_client):
    res = await async_client.post(
        "/v1/posts",
        json={"title": "Test Post", "content": "Test Content"},
    )
    assert res.status_code == 201
    assert isinstance(PostReadSchema(**res.json()), PostReadSchema)


async def test_partial_update_post(async_client, db: UnitOfWork):
    paginated = await db.posts.get_posts_with_offset(0, 5)
    post_id = paginated.model_dump()["posts"][0]["id"]

    res = await async_client.patch(
        f"/v1/posts/{post_id}",
        json={"title": "Test Post Updated"},
    )
    assert res.status_code == 200
    assert res.json().get("title") == "Test Post Updated"


async def test_partial_update_not_existing_post(async_client, db: UnitOfWork):
    post_id = uuid4()

    res = await async_client.patch(
        f"/v1/posts/{post_id}",
        json={"title": "Test Post Updated"},
    )
    assert res.status_code == 404
    assert res.json().get("error") == "post_not_found"


async def test_delete_post(async_client, db: UnitOfWork):
    paginated = await db.posts.get_posts_with_offset(0, 5)
    post_id = paginated.model_dump()["posts"][0]["id"]

    res = await async_client.delete(f"/v1/posts/{post_id}")
    assert res.status_code == 200
    assert res.json() == {"message": "Post deleted."}


async def test_delete_not_existing_post(async_client):
    post_id = uuid4()

    res = await async_client.delete(f"/v1/posts/{post_id}")

    assert res.status_code == 404
    assert res.json().get("error") == "post_not_found"
