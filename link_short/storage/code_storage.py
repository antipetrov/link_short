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

    def __init__(self, shard_id: int):
        self.shard_id = shard_id
        # self.salt_int = salt_int

    def get_id_from_code(self, code):
        try:
            shard_id, row_id, salt = hash_creator.decode(code)
        except ValueError as e:
            raise ShortCodeDecodeError()

        if not shard_id == self.shard_id:
            raise ShortCodeNotFound()

        return row_id

    async def create(self, db:AsyncConnection, url: str) -> int:
        """
        Here `create()` does not actually store code in DB, it only stores url.
        After new `url` is saved in db, it encodes `shard_id(int)+primary_key(int)+salt(int)` into hashid-code
        :param url:
        :return:
        """
        query = url_codes_table.insert().values(
            url=url,
            created=datetime.datetime.utcnow(),
        )
        async with db.begin_nested():
            try:
                insert_cursor = await db.execute(query)
                insert_record_id = insert_cursor.inserted_primary_key[0]
            except SQLAlchemyError:
                await db.rollback()
                raise ShortCodeStorageCreateError()
        #
        # try:
        #     code = hash_creator.encode(self.shard_id, insert_record_id, self.salt_int)
        # except NameError as e:
        #     # CURRENT SHARD NOT SET
        #     raise ShortCodeConfigError()

        return insert_record_id

    async def get(self, db: AsyncConnection, url_id: int) -> CodeStorageGet:
        """
        Decode `shard_id+primary_key` from code
        :param short_code:
        :return:
        """
        # row_id = self.get_id_from_code(short_code)

        query = url_codes_table.select().where(url_codes_table.c.id == url_id)
        rows_cursor = await db.execute(query)
        row = rows_cursor.first()
        if not row:
            raise ShortCodeNotFound()

        return CodeStorageGet(**row)

    async def update(self, db: AsyncConnection,  url_id: int, url: str) -> int:

        # row_id = self.get_id_from_code(short_code)

        update_query = url_codes_table.update().where(url_codes_table.c.id == url_id).values(url=url)
        rows_cursor = await db.execute(update_query)
        return rows_cursor.rowcount

    async def delete(self, db: AsyncConnection,  url_id: int) -> int:

        delete_query = url_codes_table.delete().where(url_codes_table.c.id == url_id)

        try:
            rows_cursor = await db.execute(delete_query)
        except SQLAlchemyError:
            raise ShortCodeStorageDeleteError

        return rows_cursor.rowcount
