import datetime
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from hash_creator import get_hash_creator
from config import get_settings

from db.tables import url_codes_table, url_codes_stat_table
from storage.models import CodeStorageGet

hash_creator = get_hash_creator(get_settings())


class ShortCodeCreateError(Exception):
    pass


class ShortCodeConfigError(Exception):
    pass


class ShortCodeNotFound(Exception):
    pass


class ShortCodeDecodeError(Exception):
    pass


class ShortCodeStorage:

    def __init__(self, shard_id: int, salt_int: int = None):
        self.shard_id = shard_id
        self.salt_int = salt_int

    def get_id_from_code(self, code):
        try:
            shard_id, row_id, salt = hash_creator.decode(code)
        except ValueError as e:
            raise ShortCodeDecodeError()

        if not shard_id == self.shard_id:
            raise ShortCodeNotFound()

        return code

    async def create(self, db:AsyncSession, url: str) -> str:
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
        insert_cursor = await db.execute(query)
        insert_record_id = insert_cursor.inserted_primary_key[0]

        # crud = CRUDUrlCode()
        # insert_record_id = await crud.create(self.db, url)

        try:
            code = hash_creator.encode(self.shard_id, insert_record_id, self.salt_int)
        except NameError as e:
            # CURRENT SHARD NOT SET
            raise ShortCodeConfigError()

        return code

    async def get(self, db: AsyncSession, short_code: str) -> CodeStorageGet:
        """
        Decode `shard_id+primary_key` from code
        :param short_code:
        :return:
        """
        row_id = self.get_id_from_code(short_code)

        query = url_codes_table.select().where(url_codes_table.c.id == row_id)
        rows_cursor = await db.execute(query)
        row = rows_cursor.first()
        if not row:
            raise ShortCodeNotFound()

        return CodeStorageGet(**row)

    async def update(self, db: AsyncSession,  short_code: str, url: str) -> bool:

        row_id = self.get_id_from_code(short_code)

        update_query = url_codes_table.update().where(url_codes_table.c.id == row_id).values(url=url)
        rows_cursor = await db.execute(update_query)

        return rows_cursor.rowcount > 0

    async def delete(self, db: AsyncSession,  short_code: str) -> bool:

        row_id = self.get_id_from_code(short_code)

        update_query = url_codes_table.delete().where(url_codes_table.c.id == row_id)
        rows_cursor = await db.execute(update_query)
        if rows_cursor.rowcount == 0:
            raise ShortCodeNotFound()

        return True


    # async def add_event(self, db: AsyncSession, code_id: int) -> bool:
    #     query = url_codes_stat_table.insert().values(
    #         code_id=code_id,
    #         type=
    #         created=datetime.utcnow(),
    #     )
    #     insert_cursor = await self.db.execute(query)
    #     insert_record_id = insert_cursor.inserted_primary_key[0]