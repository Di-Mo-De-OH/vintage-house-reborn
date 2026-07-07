import re
from typing import Annotated

from pydantic import AfterValidator

EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")


def validate_email(email: str) -> str:
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("올바른 이메일 형식이 아닙니다.")
    return email


EmailField = Annotated[str, AfterValidator(validate_email)]
