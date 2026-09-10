from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import ValidationError
from pytest import mark, param, raises

from app.schemas import CursorPaginationSchema, Pagination, PostCreateSchema, PostReadSchema


@mark.parametrize(
    "id, title, content, exc",
    [
        param(
            uuid4(),
            "post number: 1",
            None,
            does_not_raise(),
            id="correct_id",
        ),
        param(
            1,
            "post number: 1",
            None,
            raises(ValidationError),
            id="int_as_id",
        ),
        param(
            "12",
            "post number: 1",
            None,
            raises(ValidationError),
            id="str_as_id",
        ),
        param(
            (),
            "post number: 1",
            None,
            raises(ValidationError),
            id="tuple_as_id",
        ),
        param(
            uuid4(),
            "post number: 1",
            None,
            does_not_raise(),
            id="correct_title",
        ),
        param(
            uuid4(),
            "post number: 1",
            "Post_Content",
            does_not_raise(),
            id="correct_title_and_content",
        ),
        param(
            uuid4(),
            [],
            None,
            raises(ValidationError),
            id="list_as_title",
        ),
        param(
            uuid4(),
            "post number: 1",
            {},
            raises(ValidationError),
            id="dict_as_content",
        ),
    ],
)
async def test_post_read(
    id: UUID,
    title: str,
    content: str | None,
    exc: AbstractContextManager[object],
):
    with exc:
        PostReadSchema(
            id=id,
            title=title,
            content=content,
            created_at=datetime.now(),
        )


@mark.parametrize(
    "title, content, exc",
    [
        param("post number: 1", None, does_not_raise(), id="correct_title"),
        param("post number: 2", "Post_Content", does_not_raise(), id="correct_title_and_content"),
        param([], "Post_Content", raises(ValidationError), id="list_as_title"),
        param(None, "Post_Content", raises(ValidationError), id="none_as_title"),
        param([], {}, raises(ValidationError), id="incorrect_title_and_content"),
    ],
)
async def test_post_create(title: str, content: str | None, exc: AbstractContextManager[object]):
    with exc:
        PostCreateSchema(title=title, content=content)


@mark.parametrize(
    "page, page_size, exc",
    [
        param(1, 10, does_not_raise(), id="correct_page_and_page_size"),
        param(1, 49, does_not_raise(), id="correct_page_and_page_size_2"),
        param(1, 1, does_not_raise(), id="page_size_min_value"),
        param(1, 50, does_not_raise(), id="page_size_max_value"),
        param(0, 10, raises(ValidationError), id="zero_as_page"),
        param(-1, 10, raises(ValidationError), id="negative_as_page"),
        param(1, 0, raises(ValidationError), id="zero_as_page_size"),
        param(1, -10, raises(ValidationError), id="negative_as_page_size"),
        param(1, 51, raises(ValidationError), id="page_size_max_value_exceeded"),
    ],
)
async def test_pagination(page: int, page_size: int, exc: AbstractContextManager[object]):
    with exc:
        Pagination(page=page, page_size=page_size)


@mark.parametrize(
    "limit, cursor_id, created_at, exc",
    [
        param(5, None, None, does_not_raise(), id="correct_limit_and_cursor_id_and_created_at"),
        param(5, uuid4(), datetime.now(), does_not_raise(), id="correct_request"),
        param(1, uuid4(), datetime.now(), does_not_raise(), id="limit_at_min"),
        param(50, uuid4(), datetime.now(), does_not_raise(), id="limit_at_max"),
        param(0, uuid4(), datetime.now(), raises(ValidationError), id="limit_less_than_min"),
        param(51, uuid4(), datetime.now(), raises(ValidationError), id="limit_more_than_max"),
        param(
            5,
            uuid4(),
            None,
            raises(ValidationError),
            id="created_at_is_none_while_cursor_id_is_not_none",
        ),
        param(
            5,
            None,
            datetime.now(),
            raises(ValidationError),
            id="cursor_id_is_none_while_created_at_is_not_none",
        ),
    ],
)
async def test_cursor_pagination(
    limit: int,
    cursor_id: UUID | None,
    created_at: datetime | None,
    exc: AbstractContextManager[object],
):
    with exc:
        CursorPaginationSchema(limit=limit, cursor_id=cursor_id, created_at=created_at)
