from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.utils.validators import EmailField, NicknameField, PasswordField


class SignUpRequest(BaseModel):
    password: PasswordField = Field(examples=["Password@1"])
    confirm_password: PasswordField = Field(examples=["Password@1"])
    nickname: NicknameField = Field(examples=["테스트닉네임"])
    name: str = Field(examples=["김리본"])
    address: str | None = Field(default=None, examples=["서울 마포구 ..."])
    verify_token: str = Field(examples=["Ab3dEfGhIjKlMnOpQrStUvWx1234"])

    @model_validator(mode="after")
    def validate_confirm_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("비밀번호 및 확인 비밀번호가 일치하지 않습니다.")
        return self


class SignUpResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(examples=["01JB3X8Z9Q0K4C7D2E5F6G7H8J"])
    email: EmailField = Field(examples=["test@example.com"])
    nickname: NicknameField = Field(examples=["테스트닉네임"])
    name: str = Field(examples=["김리본"])
    address: str | None = Field(default=None, examples=["서울 마포구 ..."])
