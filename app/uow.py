from types import TracebackType
from typing import Any, Self

from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql import Executable

from app.repository.post_repo import PostRepository


class UnitOfWork:
    """Единица работы: управляет жизненным циклом сессии и репозиториев."""

    _session: AsyncSession
    posts: PostRepository

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self._session = self.session_factory()

        self.posts = PostRepository(self._session)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.close()

    async def execute(self, stmt: Executable) -> Result[Any]:
        return await self._session.execute(stmt)
