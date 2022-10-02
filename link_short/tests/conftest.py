import asyncio
from typing import Generator, Any, Tuple
import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, AsyncSession

from main import app
from db.tables import metadata, url_codes_table
from db.session import get_db
from config import get_test_settings
from main import hash_creator

settings_test = get_test_settings()

engine = create_async_engine(settings_test.DATABASE_URL)
async_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
AsyncSessionLocal = async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def db_connection() -> Generator:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    async with engine.connect() as conn:
        yield conn
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def db_session(db_connection: Generator) -> Generator[AsyncSession, Any, None]:
    transaction = await db_connection.begin()
    session = AsyncSessionLocal(bind=db_connection)
    yield session  # use the session in tests.
    transaction.rollback()
    session.close()


@pytest_asyncio.fixture(scope="module")
async def client(
    db_session: AsyncSession
) -> Generator[AsyncClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    async def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url='http://127.0.0.1:8000') as cl:
        yield cl


@pytest_asyncio.fixture(scope="module")
async def short_code_in_db(db_session:AsyncSession) -> Tuple[str, str]:
    url = 'http://test.test'
    query = url_codes_table.insert().values(
        url=url,
        created=datetime.datetime.utcnow(),
    )

    insert_cursor = await db_session.execute(query)
    insert_record_id = insert_cursor.inserted_primary_key[0]
    code = hash_creator.encode(settings_test.CURRENT_SHARD, insert_record_id, settings_test.CODE_SALT_INT)

    return code, url

