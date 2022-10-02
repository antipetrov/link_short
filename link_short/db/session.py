from asyncio import current_task

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL)
async_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
AsyncSessionLocal = async_scoped_session(async_session_factory, scopefunc=current_task)


async def get_db():
    try:
        session = AsyncSessionLocal()
        yield session
    finally:
        session.close()
