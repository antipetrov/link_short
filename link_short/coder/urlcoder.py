from hashids import Hashids
from pydantic import BaseModel


class UrlCoderData(BaseModel):
    id: int
    shard_id: int


class UrlCoder:

    def __init__(self, shard_id: int, salt: str, alphabet: str, min_length: int = 5):
        self.shard_id = shard_id

        self.coder = Hashids(
            salt=salt,
            alphabet=alphabet,
            min_length=min_length
        )

    def encode(self, code_id: int) -> str:
        return self.coder.encode(code_id, self.shard_id)

    def decode(self, code: str) -> UrlCoderData:
        try:
            code_id, shard_id = self.coder.decode(code)
        except ValueError:
            raise UrlCoderDecodeError()

        if not shard_id == self.shard_id:
            raise UrlCoderDecodeError()

        return UrlCoderData(id=code_id, shard_id=shard_id)


class UrlCoderDecodeError(Exception):
    pass