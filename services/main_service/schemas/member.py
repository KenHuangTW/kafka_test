from pydantic import BaseModel, Field, field_validator

from .base import BaseResponse


class MemberRegisterRequest(BaseModel):
    account: str = Field(min_length=1, max_length=128)
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value) != 10:
            raise ValueError("password length must be exactly 10 characters")
        return value


class MemberLoginRequest(BaseModel):
    account: str = Field(min_length=1, max_length=128)
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value) != 10:
            raise ValueError("password length must be exactly 10 characters")
        return value


class MemberAuthData(BaseModel):
    member_id: int
    token: str


class MemberRegisterResponse(BaseResponse):
    data: MemberAuthData


class MemberLoginResponse(BaseResponse):
    data: MemberAuthData
