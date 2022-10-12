from pydantic import BaseModel, AnyHttpUrl


class CreateCodeRequest(BaseModel):
    url: AnyHttpUrl


class CreateCodeResponse(BaseModel):
    code: str


class UpdateCodeRequest(BaseModel):
    code: str
    url: AnyHttpUrl


class UpdateCodeResponse(BaseModel):
    updated: bool


class GetCodeResponse(BaseModel):
    url: AnyHttpUrl
