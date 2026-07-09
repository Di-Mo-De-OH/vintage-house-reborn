import re
from typing import Annotated

from pydantic import AfterValidator

EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")

NICKNAME_PATTERN = re.compile(r"^[가-힣a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?~`]{1,8}$")

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 20

PASSWORD_LETTER_PATTERN = re.compile(r"[A-Za-z]")
PASSWORD_UPPERCASE_PATTERN = re.compile(r"[A-Z]")
PASSWORD_DIGIT_PATTERN = re.compile(r"\d")
PASSWORD_SPECIAL_PATTERN = re.compile(r"[!@#$%^&*()]")


def validate_email(email: str) -> str:
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("올바른 이메일 형식이 아닙니다.")
    return email


def validate_nickname(nickname: str) -> str:
    if not NICKNAME_PATTERN.fullmatch(nickname):
        raise ValueError("닉네임은 8자리 이하여야 입니다.")
    return nickname


def validate_password(password: str) -> str:
    if not PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH:
        raise ValueError("비밀번호는 8자리 이상 20자리 이하 입니다.")
    if not PASSWORD_LETTER_PATTERN.search(password):
        raise ValueError("비밀번호는 영문을 포함해야 합니다.")
    if not PASSWORD_UPPERCASE_PATTERN.search(password):
        raise ValueError("비밀번호는 대문자 하나를 포함해야 합니다.")
    if not PASSWORD_DIGIT_PATTERN.search(password):
        raise ValueError("비밀번호는 숫자를 포함해야 합니다.")
    if not PASSWORD_SPECIAL_PATTERN.search(password):
        raise ValueError("비밀번호는 특수문자를 포함해야 합니다.")
    return password


PasswordField = Annotated[str, AfterValidator(validate_password)]
NicknameField = Annotated[str, AfterValidator(validate_nickname)]
EmailField = Annotated[str, AfterValidator(validate_email)]
