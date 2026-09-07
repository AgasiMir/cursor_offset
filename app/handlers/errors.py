from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.python_exceptions import PostNotFoundException
from app.handlers.schemas import ErrorResponse


def build_error_response(error: str, message: str, status_code: int) -> JSONResponse:
    payload = ErrorResponse(error=error, message=message)
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def post_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return build_error_response(
        error="post_not_found",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(PostNotFoundException, post_not_found_handler)
