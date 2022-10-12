from datetime import datetime
from pydantic import BaseModel, AnyHttpUrl


class CodeStorageGet(BaseModel):
    id: int
    url: str
    created: datetime