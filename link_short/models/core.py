from pydantic import BaseModel, AnyHttpUrl


class CreateUrlRequest(BaseModel):
    url: AnyHttpUrl


class CreateUrlResponse(BaseModel):
    code: str


class UpdateUrlRequest(BaseModel):
    code: str
    url: AnyHttpUrl


class UpdateUrlResponse(BaseModel):
    updated: bool
