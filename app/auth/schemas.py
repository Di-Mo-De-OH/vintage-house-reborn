import re

from pydantic import BaseModel, field_validator

from app.core.utils.validators import EmailField


class SendEmailRequest(BaseModel):
    email: EmailField


class VerifyEmailRequest(BaseModel):
    email: EmailField
    code: str

    @field_validator("code")
    @classmethod
    def validate_code(cls, code: str) -> str:
        if not re.fullmatch(r"\d{6}", code):
            raise ValueError("인증 코드는 6자리 숫자여야 합니다.")
        return code


class VerifyEmailResponse(BaseModel):
    verify_token: str
