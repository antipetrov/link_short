from sqlalchemy.ext.asyncio import AsyncConnection

from fastapi import FastAPI, HTTPException, Depends

from coder.urlcoder import UrlCoder, UrlAddress, UrlCoderDecodeError
from models.core import CreateCodeRequest, CreateCodeResponse, UpdateCodeRequest, UpdateCodeResponse, GetCodeResponse,\
                        GetCodeStatResponse, DeleteCodeResponse

from config import get_settings
from db.engine import get_db
from storage.short_code_stat_crud import ShortCodeStatCRUD
from storage.short_code_crud import ShortCodeCRUD, ShortCodeNotFound, ShortCodeDecodeError
from storage.errors import ShortCodeStorageError, ShortCodeStorageConfigError

app = FastAPI()
settings = get_settings()

code_storage = ShortCodeCRUD()
code_stat = ShortCodeStatCRUD()

coder = UrlCoder(
    shard_id=settings.CURRENT_SHARD,
    salt=settings.CODE_SALT,
    alphabet=settings.CODE_ALPHABET,
    min_length=settings.CODE_MIN_LENGTH
)


@app.post('/urls/')
async def create_code(item: CreateCodeRequest, db: AsyncConnection = Depends(get_db)):
    """
    Creates new short_code for url
    :param item:
    :param db:
    :return:
    """
    async with db.begin_nested():
        try:
            url_id = await code_storage.create(db, item.url)
            await db.commit()
        except ShortCodeStorageConfigError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Service config error")

    code = coder.encode(url_id)

    return CreateCodeResponse(code=code)


@app.get('/urls/{short_code}')
async def get_code(short_code: str, db: AsyncConnection = Depends(get_db)):
    """
    Shows url stored in short_code
    :param short_code:
    :param db:
    :return:
    """

    try:
        url_address: UrlAddress = coder.decode(short_code)
        url_data = await code_storage.get(db, url_address.id)
    except (ShortCodeNotFound, UrlCoderDecodeError):
        raise HTTPException(status_code=404, detail="Code not found")

    await code_stat.save_event(db, url_data.id)

    return GetCodeResponse(url=url_data.url)


@app.get('/urls/{short_code}/stats')
async def get_code_stat(short_code: str, db: AsyncConnection = Depends(get_db)):
    """
    Shows view count for short_code in the actual period
    :param short_code:
    :param db:
    :return:
    """
    try:
        code_data: UrlAddress = coder.decode(short_code)
    except UrlCoderDecodeError:
        raise HTTPException(status_code=404, detail="Code not found")

    count = await code_stat.actual_events_count(db, code_data.id, settings.STAT_ACTUAL_HOURS)
    return GetCodeStatResponse(count=count)


@app.put('/urls/{short_code}')
async def update_code(short_code: str, item: UpdateCodeRequest, db: AsyncConnection = Depends(get_db)):
    """
    Update url stored in short_code
    :param short_code:
    :param item:
    :param db:
    :return:
    """

    db.begin_nested()
    try:
        code_data: UrlAddress = coder.decode(short_code)
        update_count = await code_storage.update(db, code_data.id, item.url)
        await db.commit()
    except (ShortCodeNotFound, ShortCodeDecodeError):
        await db.rollback()
        raise HTTPException(status_code=404, detail="Code not found")

    return UpdateCodeResponse(updated=update_count > 0)


@app.delete('/urls/{short_code}')
async def delete_code(short_code: str, db: AsyncConnection = Depends(get_db)):
    """
    Deletes short code
    :param short_code:
    :param db:
    :return:
    """

    db.begin_nested()
    try:
        code_data: UrlAddress = coder.decode(short_code)

        delete_count = await code_storage.delete(db, code_data.id)
        deleted_stat_count = await code_stat.delete(db, code_data.id)
        await db.commit()
    except ShortCodeStorageError:
        await db.rollback()
        raise HTTPException(status_code=404, detail="Code not found")

    return DeleteCodeResponse(deleted=delete_count > 0)