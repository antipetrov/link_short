import databases
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import FastAPI, HTTPException, Depends
from models.core import CreateUrlRequest, CreateUrlResponse, UpdateUrlRequest, UpdateUrlResponse


from config import get_settings
from db.session import get_db
from storage.code_stat import ShortCodeStat
from storage.code_storage import ShortCodeStorage, ShortCodeNotFound, ShortCodeConfigError, ShortCodeDecodeError


app = FastAPI()
settings = get_settings()

code_storage = ShortCodeStorage(
    shard_id=settings.CURRENT_SHARD,
    salt_int=settings.CODE_SALT_INT
)

code_stat = ShortCodeStat(get_db())



@app.post('/urls/')
async def create_code(item: CreateUrlRequest, db:AsyncSession = Depends(get_db)):

    try:
        code = await code_storage.create(db, item.url)
    except ShortCodeConfigError:
        raise HTTPException(status_code=500, detail="Service config error")

    return CreateUrlResponse(code=code)


@app.get('/urls/{short_code}')
async def get_code(short_code: str, db: AsyncSession = Depends(get_db)):
    try:
        code_data = await code_storage.get(db, short_code)
    except (ShortCodeNotFound, ShortCodeDecodeError):
        raise HTTPException(status_code=404, detail="Code not found")

    stat_saved = await code_stat.save_event(db, code_data.id)

    return {"url": code_data.url}


@app.get('/urls/{short_code}/stats')
async def get_code_stat(short_code: str, db: AsyncSession = Depends(get_db)):
    code_id = code_storage.get_id_from_code(short_code)
    count = await code_stat.count_events_24h(db, code_id)
    return {'visit_count': count}


@app.put('/urls/{short_code}')
async def update_code(short_code: str, item: UpdateUrlRequest, db: AsyncSession = Depends(get_db)):
    try:
        updated = code_storage.update(db, short_code, item.url)
    except (ShortCodeNotFound, ShortCodeDecodeError):
        raise HTTPException(status_code=404, detail="Code not found")

    return {"updated": updated}


@app.delete('/urls/{short_code}')
async def delete_code(short_code: str, db: AsyncSession = Depends(get_db)):
    try:
        deleted = code_storage.update(db, short_code)
    except (ShortCodeNotFound, ShortCodeDecodeError):
        raise HTTPException(status_code=404, detail="Code not found")

    return {"status": deleted}