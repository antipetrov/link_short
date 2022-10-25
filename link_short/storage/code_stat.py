from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection

from db.tables import url_codes_stat_table, EventTypeEnum
from storage.code_storage import ShortCodeNotFound


class ShortCodeStat:

    def __init__(self, actual_hours: int = 24):
        self.actual_hours: int = actual_hours

    async def save_event(self, db: AsyncConnection, code_id: int) -> Optional[int]:
        """
        Save single event in table.
        :param db:
        :param code_id:
        :return: event_id
        """

        query = url_codes_stat_table.insert().values(
            url_code_id=code_id,
            event_time=datetime.utcnow(),
        )

        async with db.begin_nested():  # here begin_nested acts like begin if no outer transacion started
            try:
                insert_cursor = await db.execute(query)
                insert_record_id = insert_cursor.inserted_primary_key[0]
            except SQLAlchemyError:
                return None
        return insert_record_id

    async def list_events(self, db: AsyncConnection, code_id: int) -> List:
        """
        Get events from table
        :param db:
        :param code_id:
        :return:
        """
        query = url_codes_stat_table.select().where(
            url_codes_stat_table.c.code_id == code_id
        )

        rows_cursor = await db.execute(query)
        rows = rows_cursor.all()
        if not rows:
            raise ShortCodeNotFound()

        return rows

    async def count_events_actual(self, db: AsyncConnection, code_id: int) -> int:
        """
        returns event-count in `actual_hours` interval
        :param db:
        :param code_id:
        :return:
        """
        from_time = datetime.utcnow() - timedelta(hours=self.actual_hours)
        query = select([func.count()]).select_from(url_codes_stat_table).where(
            url_codes_stat_table.c.url_code_id == code_id,
            url_codes_stat_table.c.event_time > from_time
        )

        rows_cursor = await db.execute(query)
        row = rows_cursor.first()
        if not row:
            raise ShortCodeNotFound()

        return row[0]

    async def delete(self, db: AsyncConnection, code_id: int) -> int:
        """
        Delete stat for single url (when code itself is deleted)
        :param db:
        :param code_id:
        :return:
        """

        delete_query = url_codes_stat_table.delete().where(url_codes_stat_table.c.url_code_id == code_id)
        delete_cursor = await db.execute(delete_query)
        return delete_cursor.rowcount

    async def cleanup(self, db: AsyncConnection, without_actual: bool = True) -> int:
        """
        Mass delete events from db
        :param db:
        :param without_actual: delete everything older than `self.actual_hours`
        :return:
        """
        delete_query = url_codes_stat_table.delete()

        if without_actual:
            from_time = datetime.utcnow() - timedelta(hours=self.actual_hours)
            delete_query = delete_query.where(
                url_codes_stat_table.c.event_time < from_time
            )

        delete_cursor = await db.execute(delete_query)
        return delete_cursor.rowcount
