import databases
from config import Settings, get_settings, get_test_settings


def get_db_by_url(url: str) -> databases.Database:
    return databases.Database(url)


def get_db() -> databases.Database:
    return get_db_by_url(get_settings().DATABASE_URL)


def get_test_db() -> databases.Database:
    return get_db_by_url(get_test_settings().DATABASE_URL)
