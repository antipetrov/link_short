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

