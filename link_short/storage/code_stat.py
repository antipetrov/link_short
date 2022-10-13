from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.tables import url_codes_stat_table, EventTypeEnum
from storage.code_storage import ShortCodeNotFound

class ShortCodeStat:

    async def save_event(self, db: AsyncSession, code_id: int) -> bool:

        query = url_codes_stat_table.insert().values(
            url_code_id=code_id,
            event_time=datetime.utcnow(),
        )
        insert_cursor = await db.execute(query)
        insert_record_id = insert_cursor.inserted_primary_key[0]

        return insert_record_id is not None

    async def list_events(self, db: AsyncSession, code_id: int) -> List:
        query = url_codes_stat_table.select().where(
            url_codes_stat_table.c.code_id == code_id
        )

        rows_cursor = await db.execute(query)
        rows = rows_cursor.all()
        if not rows:
            raise ShortCodeNotFound()

        return rows

    async def count_events_24h(self, db: AsyncSession, code_id: int) -> int:
        from_time = datetime.utcnow() - timedelta(hours=24)
        # query = url_codes_stat_table.select().where(
        #     url_codes_stat_table.c.url_code_id == code_id,
        #     url_codes_stat_table.c.event_time > from_time
        # )


        query = select([func.count()]).select_from(url_codes_stat_table).where(
            url_codes_stat_table.c.url_code_id == code_id,
            url_codes_stat_table.c.event_time > from_time
        )

        rows_cursor = await db.execute(query)
        row = rows_cursor.first()
        if not row:
            raise ShortCodeNotFound()

        return row[0]
