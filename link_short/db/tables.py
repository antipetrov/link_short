import enum

import sqlalchemy

metadata = sqlalchemy.MetaData()

url_codes_table = sqlalchemy.Table(
    "url_codes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("url", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("created", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Index("created_idx", "created", unique=False),
)


class EventTypeEnum(enum.Enum):
    get = 1,
    create = 2,
    update = 3,


url_codes_stat_table = sqlalchemy.Table(
    "url_codes_stat",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("url_code_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("event_time", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Index("url_code_idx", "url_code_id", unique=False),
    sqlalchemy.Index("event_time_idx", "event_time", unique=False),
)

