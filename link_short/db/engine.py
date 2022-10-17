import asyncio
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine, AsyncEngine, AsyncConnection
from sqlalchemy.orm.scoping import ScopedSession

from config import get_settings, get_test_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL)
engine_sync = create_engine(settings.DATABASE_SYNC_URL)


async def get_db() -> AsyncConnection:
    async with engine.connect() as connection:
        yield connection


def get_db_sync() -> Connection:
    with engine_sync.connect() as connection:
        yield connection


async def get_test_db() -> AsyncConnection:
    engine_test = create_async_engine(get_test_settings().DATABASE_URL)
    async with engine_test.connect() as connection:
        yield connection


def get_test_db_sync() -> Connection:
    with engine_sync.connect() as connection:
        yield connection

