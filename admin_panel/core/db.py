from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from admin_panel.core.config import settings

engine = create_async_engine(
    settings.postgres.database_url,
    pool_pre_ping=True,
    echo=settings.postgres.database_echo,
    pool_size=settings.postgres.database_pool_size,
    max_overflow=settings.postgres.database_max_overflow,
)

AsyncDBSession = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncDBSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    await engine.dispose()
