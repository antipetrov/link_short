from fastapi import Depends

from hashids import Hashids
import settings

from db.session import engine

hash_creator = Hashids(salt=settings.CODE_SEED,
                       alphabet=settings.CODE_ALPHABET,
                       min_length=settings.CODE_MIN_LENGTH)

class ShortCodeStorage():

    def __init__(self, database_settings=Depends(settings.DATABASE_URL)):
        pass

    def save(self, url:str) -> str:
        pass

    def load(self, short_code: str) -> str:
        pass

    def connect(self):
        engine.connect(settings.DATABASE_URL)

    def disconnect(self):
        pass