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


async def async_stat_cleanup(actual: bool):
    from storage.short_code_stat_crud import ShortCodeStatCRUD
    engine = await create_engine()
    async with engine.connect() as connection:
        async with connection.begin():
            try:
                deleted_count = await ShortCodeStatCRUD().cleanup(db=connection, without_actual=not actual)
                await connection.commit()
            except SQLAlchemyError:
                await connection.rollback()

    sys.stdout.write(f"Stat cleanup completed. Actual records cleaned: {actual} Stat records delete-result: {deleted_count}")


@cli.command()
def stat_cleanup(actual: bool = typer.Option(False, help="delete stat older than actual period")):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_stat_cleanup(actual))


if __name__ == "__main__":
    cli()
