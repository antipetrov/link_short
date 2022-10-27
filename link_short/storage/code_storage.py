import datetime
from typing import Tuple

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection

from config import get_settings

from db.tables import url_codes_table
from storage.models import CodeStorageGet
from storage.errors import ShortCodeStorageCreateError, ShortCodeDecodeError, ShortCodeNotFound, ShortCodeStorageConfigError,\
                           ShortCodeStorageDeleteError


class ShortCodeStorage:

    def __init__(self,):
        pass

    async def create(self, db:AsyncConnection, url: str) -> int:
        """
        Here `create()` does not actually store short code in DB, it only stores url itself.
        :param db:
        :param url:
        :return:
        """
        query = url_codes_table.insert().values(
            url=url,
            created=datetime.datetime.utcnow(),
        )

        try:
            insert_cursor = await db.execute(query)
            insert_record_id = insert_cursor.inserted_primary_key[0]
        except SQLAlchemyError:
            raise ShortCodeStorageCreateError()

        return insert_record_id

    async def get(self, db: AsyncConnection, url_id: int) -> CodeStorageGet:
        """
        Decode `shard_id+primary_key` from code
        :param db:
        :param short_code:
        :return:
        """

        query = url_codes_table.select().where(url_codes_table.c.id == url_id)
        rows_cursor = await db.execute(query)
        row = rows_cursor.first()
        if not row:
            raise ShortCodeNotFound()

        return CodeStorageGet(**row)

    async def update(self, db: AsyncConnection,  url_id: int, url: str) -> int:
        """
        Updates existing url-record
        :param db:
        :param url_id:
        :param url:
        :return:
        """

        update_query = url_codes_table.update().where(url_codes_table.c.id == url_id).values(url=url)
        rows_cursor = await db.execute(update_query)
        return rows_cursor.rowcount

    async def delete(self, db: AsyncConnection,  url_id: int) -> int:
        """
        delete existing url-record
        :param db:
        :param url_id:
        :return:
        """

        delete_query = url_codes_table.delete().where(url_codes_table.c.id == url_id)

        try:
            rows_cursor = await db.execute(delete_query)
        except SQLAlchemyError:
            raise ShortCodeStorageDeleteError

        return rows_cursor.rowcount
