from pydantic import BaseSettings


class Settings(BaseSettings):

    CODE_SEED: str = 'ABCDEF'
    CODE_MIN_LENGTH: int = 4
    CODE_ALPHABET: str = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    CODE_SALT_INT = 156
    CURRENT_SHARD: int = 1

    #working db
    DATABASE_URL: str = "postgresql+asyncpg://postgres:testpass@127.0.0.1:5432/url_db"
    # this is for sync connection to call create_tables()
    DATABASE_UTIL_URL: str = "postgresql://postgres:testpass@127.0.0.1:5432/url_db"


class TestSettings(Settings):
    #test db
    DATABASE_URL: str = "postgresql+asyncpg://postgres:testpass@127.0.0.1:5432/url_test_db"
    # this is for sync connection to call create_tables()
    DATABASE_UTIL_URL: str = "postgresql://postgres:testpass@127.0.0.1:5432/url_test_db"


def get_settings() -> Settings:
    return Settings()


def get_test_settings() -> Settings:
    return TestSettings()