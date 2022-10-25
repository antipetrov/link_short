import asyncio
from typing import Generator, Any, Tuple
import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, AsyncConnection

from coder.urlcoder import UrlCoder
from main import app
from db.tables import metadata, url_codes_table, url_codes_stat_table
from db.engine import get_db
from config import get_test_settings
from hash_creator import hash_creator

settings_test = get_test_settings()


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def db_connection() -> AsyncConnection:
    engine = create_async_engine(settings_test.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    async with engine.connect() as conn:
        yield conn
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def db_test_engine(db_connection: AsyncConnection) -> Generator[AsyncEngine, Any, None]:
    transaction = await db_connection.begin()
    yield db_connection  # use connection in tests
    await transaction.rollback()


@pytest_asyncio.fixture(scope="module")
async def client(
    db_test_engine: AsyncSession
) -> Generator[AsyncClient, Any, None]:

    async def _get_test_db():
        try:
            yield db_test_engine
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url='http://127.0.0.1:8000') as cl:
        yield cl

@pytest_asyncio.fixture(scope="module")
async def coder() -> UrlCoder:

    coder = UrlCoder(
        shard_id=settings_test.CURRENT_SHARD,
        salt=settings_test.CODE_SALT,
        alphabet=settings_test.CODE_ALPHABET,
        min_length=settings_test.CODE_MIN_LENGTH,
    )

    return coder

@pytest_asyncio.fixture(scope="function")
async def short_code_in_db(db_test_engine: AsyncEngine, coder: UrlCoder) -> Tuple[str, str, int]:
    url = 'http://test.test'
    query = url_codes_table.insert().values(
        url=url,
        created=datetime.datetime.utcnow(),
    )

    insert_cursor = await db_test_engine.execute(query)
    insert_record_id = insert_cursor.inserted_primary_key[0]

    code = coder.encode(insert_record_id)

    return code, url, insert_record_id


@pytest_asyncio.fixture(scope="function")
async def short_code_stat_in_db(db_test_engine: AsyncEngine, short_code_in_db: Tuple) -> int:

    code, url, code_id = short_code_in_db
    query_stat = url_codes_stat_table.insert().values(
        url_code_id=code_id,
        event_time=datetime.datetime.utcnow(),
    )

    insert_stat_cursor = await db_test_engine.execute(query_stat)

    return insert_stat_cursor.inserted_primary_key[0]


@pytest_asyncio.fixture(scope="function")
async def short_code_stat_in_db_yesterday(db_test_engine: AsyncEngine, short_code_in_db: Tuple) -> int:

    code, url, code_id = short_code_in_db
    query_stat = url_codes_stat_table.insert().values(
        url_code_id=code_id,
        event_time=datetime.datetime.utcnow() - datetime.timedelta(hours=25),
    )

    insert_stat_cursor = await db_test_engine.execute(query_stat)

    return insert_stat_cursor.inserted_primary_key[0]
