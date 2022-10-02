from fastapi import Depends
from hashids import Hashids
from config import Settings, get_settings


def get_hash_creator(settings:Settings = Depends(get_settings)):
    return Hashids(
        salt=settings.CODE_SEED,
        alphabet=settings.CODE_ALPHABET,
        min_length=settings.CODE_MIN_LENGTH
    )

hash_creator = get_hash_creator(get_settings())