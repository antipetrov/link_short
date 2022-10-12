from fastapi import Depends
from hashids import Hashids
from config import Settings, get_settings


def get_hash_creator(settings: Settings):
    hash_creator = Hashids(
        salt=settings.CODE_SEED,
        alphabet=settings.CODE_ALPHABET,
        min_length=settings.CODE_MIN_LENGTH
    )

    return hash_creator


hash_creator = get_hash_creator(get_settings())