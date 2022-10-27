import asyncio
import sys

import typer
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine

from config import get_settings, get_test_settings
from db.tables import metadata


cli = typer.Typer()
settings = get_settings()
settings_test = get_test_settings()
loop = asyncio.get_event_loop()


async def create_engine():
    return create_async_engine(get_settings().DATABASE_URL)


@cli.command()
def create_db():
    engine = sqlalchemy.create_engine(
        settings.DATABASE_SYNC_URL,
    )
    metadata.create_all(engine)
    sys.stdout.write(f"DB creation completed.")


@cli.command()
def drop_db():
    engine = sqlalchemy.create_engine(
        settings.DATABASE_SYNC_URL,
    )
    metadata.drop_all(engine)
    sys.stdout.write(f"DB drop completed.")


@cli.command()
def create_test_db():
    engine = sqlalchemy.create_engine(
        settings_test.DATABASE_SYNC_URL,
    )
    metadata.create_all(engine)
    sys.stdout.write(f"TestDB creation completed.")


@cli.command()
def drop_test_db():
    engine = sqlalchemy.create_engine(
        settings_test.DATABASE_SYNC_URL,
    )
    metadata.drop_all(engine)
    sys.stdout.write(f"TestDB drop completed.")


async def async_stat_cleanup():
    from storage.short_code_stat_crud import ShortCodeStatCRUD
    engine = await create_engine()
    async with engine.connect() as connection:
        with connection.begin():
            try:
                deleted_count = await ShortCodeStatCRUD().cleanup(db=connection, without_actual=True)
                connection.commit()
            except SQLAlchemyError:
                connection.rollback()

    sys.stdout.write(f"Stat cleanup completed. Stat records delete-result: {deleted_count}")


@cli.command()
def stat_cleanup():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_stat_cleanup())


if __name__ == "__main__":
    cli()