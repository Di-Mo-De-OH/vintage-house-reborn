import re

from pydantic import BaseModel, Field, field_validator

from app.core.utils.validators import EmailField, NicknameField, PasswordField


class SendEmailRequest(BaseModel):
    email: EmailField = Field(examples=["test@example.com"])


class VerifyEmailRequest(BaseModel):
    email: EmailField = Field(examples=["test@example.com"])
    code: str = Field(examples=["123456"])

    @field_validator("code")
    @classmethod
    def validate_code(cls, code: str) -> str:
        if not re.fullmatch(r"\d{6}", code):
            raise ValueError("인증 코드는 6자리 숫자여야 합니다.")
        return code


class VerifyEmailResponse(BaseModel):
    verify_token: str = Field(examples=["Ab3dEfGhIjKlMnOpQrStUvWx1234"])


class SignUpRequest(BaseModel):
    email: EmailField = Field(examples=["test@example.com"])
    password: PasswordField = Field(examples=["Password@1"])
    nickname: NicknameField = Field(examples=["테스트닉네임"])
    name: str = Field(examples=["김리본"])
    address: str | None = Field(default=None, examples=["서울 마포구 ..."])
    verify_token: str = Field(examples=["Ab3dEfGhIjKlMnOpQrStUvWx1234"])
