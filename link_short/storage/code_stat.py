from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from db.tables import url_codes_stat_table, EventTypeEnum
from storage.code_storage import ShortCodeNotFound

class ShortCodeStat:

    async def save_event(self, db: AsyncSession, code_id: int, type: EventTypeEnum=EventTypeEnum.get) -> bool:

        query = url_codes_stat_table.insert().values(
            code_id=code_id,
            type=type,
            created=datetime.utcnow(),
        )
        insert_cursor = await db.execute(query)
        # insert_record_id = insert_cursor.inserted_primary_key[0]

        return False

    async def list_events(self, db: AsyncSession, code_id: int) -> List:
        query = url_codes_stat_table.select().where(
            url_codes_stat_table.c.code_id == code_id
        )

        rows_cursor = db.execute(query)
        rows = rows_cursor.all()
        if not rows:
            raise ShortCodeNotFound()

        return rows

    async def count_events_24h(self, db: AsyncSession, code_id: int) -> int:
        from_time = datetime.utcnow() - timedelta(hours=24)
        query = url_codes_stat_table.select(
            func.count(url_codes_stat_table.c.id)
        ).where(
            url_codes_stat_table.c.id == code_id,
            url_codes_stat_table.c.event_time > from_time
        )

        rows_cursor = db.execute(query)
        rows = rows_cursor.first()
        if not rows:
            raise ShortCodeNotFound()

        return rows
