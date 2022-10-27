from hashids import Hashids
from pydantic import BaseModel


class UrlCoderDecodeError(Exception):
    pass


class UrlAddress(BaseModel):
    """
    Where url is stored (shard_id + primary_key)
    """
    id: int
    shard_id: int


class UrlCoder:
    """
    Wrapper around hashids encoder - stores encoding settings & wraps decode result into Pydantic UrlAddress model
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

    def decode(self, code: str) -> UrlAddress:
        """
        decodes code string into UrlAddress
        also validates whether the decoder shard id == current shard_id
        :param code:
        :return:
        """

        try:
            code_id, shard_id = self.code_provider.decode(code)
        except ValueError:
            raise UrlCoderDecodeError()

        if not shard_id == self.shard_id:
            raise UrlCoderDecodeError()

        return UrlAddress(id=code_id, shard_id=shard_id)
