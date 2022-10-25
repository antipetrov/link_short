from hashids import Hashids
from pydantic import BaseModel


class UrlCoderData(BaseModel):
    id: int
    shard_id: int


class UrlCoder:
    """
    Wrapper around hashids encoder - stores current settings & wraps decode result into Pydantic model
    """

    def __init__(self, shard_id: int, salt: str, alphabet: str, min_length: int = 5):
        self.shard_id = shard_id

        self.code_provider = Hashids(
            salt=salt,
            alphabet=alphabet,
            min_length=min_length
        )

    def encode(self, code_id: int) -> str:
        return self.code_provider.encode(code_id, self.shard_id)

    def decode(self, code: str) -> UrlCoderData:
        try:
            code_id, shard_id = self.code_provider.decode(code)
        except ValueError:
            raise UrlCoderDecodeError()

        if not shard_id == self.shard_id:
            raise UrlCoderDecodeError()

        return UrlCoderData(id=code_id, shard_id=shard_id)


class UrlCoderDecodeError(Exception):
    pass