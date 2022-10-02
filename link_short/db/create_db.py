
from database import create_tables, create_test_tables
import asyncio
import sqlalchemy
import settings
metadata = sqlalchemy.MetaData()


def create_tables():
    engine = sqlalchemy.create_engine(
        settings.DATABASE_UTIL_URL,
    )
    metadata.create_all(engine)


def create_test_tables():
    engine = sqlalchemy.create_engine(
        settings.DATABASE_TEST_UTIL_URL,
    )
    metadata.create_all(engine)


def drop_test_tables():
    engine = sqlalchemy.create_engine(
        settings.DATABASE_TEST_UTIL_URL,
    )
    metadata.drop_all(engine)


create_tables()
create_test_tables()
