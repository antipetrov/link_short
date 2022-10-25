from pydantic import BaseModel, AnyHttpUrl


class CreateCodeRequest(BaseModel):
    url: AnyHttpUrl


class CreateCodeResponse(BaseModel):
    code: str


class UpdateCodeRequest(BaseModel):
    url: AnyHttpUrl


class UpdateCodeResponse(BaseModel):
    updated: bool


class DeleteCodeResponse(BaseModel):
    deleted: bool


class GetCodeResponse(BaseModel):
    url: AnyHttpUrl


class GetCodeStatResponse(BaseModel):
    count: int
