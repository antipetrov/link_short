import typer
import sqlalchemy
from config import get_settings, get_test_settings
from db.tables import metadata

cli = typer.Typer()
settings = get_settings()
settings_test = get_test_settings()

@cli.command()
def create_db():
    engine = sqlalchemy.create_engine(
        settings.DATABASE_UTIL_URL,
    )
    metadata.create_all(engine)


@cli.command()
def drop_db():
    engine = sqlalchemy.create_engine(
        settings.DATABASE_UTIL_URL,
    )
    metadata.drop_all(engine)


@cli.command()
def create_test_db():
    engine = sqlalchemy.create_engine(
        settings_test.DATABASE_UTIL_URL,
    )
    metadata.create_all(engine)


@cli.command()
def drop_test_db():
    engine = sqlalchemy.create_engine(
        settings_test.DATABASE_UTIL_URL,
    )
    metadata.drop_all(engine)


if __name__ == "__main__":
    cli()