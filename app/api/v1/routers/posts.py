import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pyrate_limiter import Duration, Limiter, Rate

from app.api.dependencies import PaginationDep, PostServiceDep
from app.api.rate_limit import RateLimiter
from app.config import settings
from app.handlers.schemas import ErrorResponse
from app.schemas import (
    PostCreateSchema,
    PostPartialUpdateSchema,
    PostReadSchema,
    PostReadSchemaWithCursor,
    PostReadSchemaWithPagination,
)

# В тестовой среде (ENVIRONMENT=TEST) лимитер не подключается, чтобы не мешать тестам.
# Это надёжнее, чем мокать RateLimiter через import-order/sys.modules — хрупко.
_dependencies: list = []
if settings.ENVIRONMENT != "TEST":
    _dependencies.append(Depends(RateLimiter(limiter=Limiter(Rate(5, Duration.SECOND * 2)))))

router = APIRouter(prefix="/v1/posts", tags=["posts 📫📬📭"], dependencies=_dependencies)


@router.get("/offset", response_model=PostReadSchemaWithPagination)
async def get_posts_offset(posts: PostServiceDep, pagination: PaginationDep):
    return await posts.get_posts_with_offset(pagination=pagination)


@router.get("/cursor", response_model=PostReadSchemaWithCursor)
async def get_post_cursor(
    posts: PostServiceDep,
    pagination: PaginationDep,
    created_at: datetime | None = None,
    cursor_id: uuid.UUID | None = None,
):
    return await posts.get_posts_with_cursor(
        limit=pagination.page_size,
        created_at=created_at,
        cursor_id=cursor_id,
    )


@router.get(
    "/{post_uuid}",
    response_model=PostReadSchema,
    summary="Get post by uuid",
    description="Returns a detailed post by uuid.",
    responses={
        404: {
            "description": "Post was not found.",
            "model": ErrorResponse,
        },
    },
)
async def get_post_by_uuid(posts: PostServiceDep, post_uuid: uuid.UUID):
    return await posts.get_post_by_uuid(post_id=post_uuid)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PostReadSchema)
async def create_post(posts: PostServiceDep, post: PostCreateSchema):
    return await posts.create_post(post=post)


@router.patch(
    "/{post_uuid}",
    response_model=PostReadSchema,
    summary="Update post by uuid",
    description="Updates a post by uuid.",
    responses={
        404: {
            "description": "Post was not found.",
            "model": ErrorResponse,
        },
    },
)
async def update_post(posts: PostServiceDep, post_uuid: uuid.UUID, post: PostPartialUpdateSchema):
    return await posts.partial_update_post(post_id=post_uuid, post=post)


@router.delete(
    "/{post_uuid}",
    summary="Delete post by uuid",
    description="Deletes a post by uuid.",
    responses={
        404: {
            "description": "Post was not found.",
            "model": ErrorResponse,
        },
    },
)
async def delete_post(posts: PostServiceDep, post_uuid: uuid.UUID):
    return await posts.delete_post(post_id=post_uuid)
