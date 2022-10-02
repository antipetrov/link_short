import datetime

import databases
import sqlalchemy.orm
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, AnyHttpUrl


from config import Settings, get_settings, get_test_settings
from db.tables import url_codes_table
from db.session import get_db
from hash_creator import hash_creator


class CreateCodeBody(BaseModel):
    url: AnyHttpUrl

class UpdateUrlBody(BaseModel):
    url: AnyHttpUrl


app = FastAPI()
settings = get_settings()


@app.post('/urls/')
async def create_code(item: CreateCodeBody, db:sqlalchemy.orm.Session = Depends(get_db)):

    query = url_codes_table.insert().values(
        url=item.url,
        created=datetime.datetime.utcnow(),
    )
    insert_cursor = await db.execute(query)
    insert_record_id = insert_cursor.inserted_primary_key[0]
    try:
        code = hash_creator.encode(settings.CURRENT_SHARD, insert_record_id, settings.CODE_SALT_INT)
    except NameError as e:
        # CURRENT SHARD NOT SET
        raise HTTPException(status_code=500, detail="Service config error")
    return {"code": code}


@app.get('/urls/{short_code}')
async def get_code(short_code: str, db: databases.Database = Depends(get_db)):

    try:
        shard_id, row_id, salt = hash_creator.decode(short_code)
    except ValueError:
        raise HTTPException(status_code=404, detail="Code not found")

    if not shard_id == settings.CURRENT_SHARD:
        raise HTTPException(status_code=404, detail="Code not found")

    query = url_codes_table.select().where(url_codes_table.c.id==row_id)
    rows_cursor = await db.execute(query)
    rows = rows_cursor.all()
    if not rows:
        raise HTTPException(status_code=404, detail="Code not found")

    return {"url": rows[0].url}


@app.get('/urls/{short_code}/stats')
async def get_code_stat(short_code: str, db: databases.Database = Depends(get_db)):
    return {"url": short_code}


@app.put('/urls/{short_code}')
async def update_code(short_code: str, item: UpdateUrlBody, db: databases.Database = Depends(get_db)):

    try:
        shard_id, row_id, salt = hash_creator.decode(short_code)
    except ValueError:
        raise HTTPException(status_code=404, detail="Code not found")

    if not shard_id == settings.CURRENT_SHARD:
        raise HTTPException(status_code=404, detail="Code not found")

    update_query = url_codes_table.update().where(url_codes_table.c.id == row_id).values(url=item.url)
    rows_cursor = await db.execute(update_query)
    if rows_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Code not found")

    return {"status": "ok"}


@app.delete('/urls/{short_code}')
async def delete_code(short_code: str, db: databases.Database = Depends(get_db)):
    try:
        shard_id, row_id, salt = hash_creator.decode(short_code)
    except ValueError:
        raise HTTPException(status_code=404, detail="Code not found")

    if not shard_id == settings.CURRENT_SHARD:
        raise HTTPException(status_code=404, detail="Code not found")

    delete_query = url_codes_table.delete().where(url_codes_table.c.id == row_id)
    delete_cursor = await db.execute(delete_query)
    if delete_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Code not found")

    return {"status": "deleted"}