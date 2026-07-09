import pytest
from pydantic import ValidationError

from app.auth.schemas.email import SendEmailRequest, VerifyEmailRequest


def test_send_email_request_valid() -> None:
    request = SendEmailRequest(email="test@example.com")
    assert request.email == "test@example.com"


def test_send_email_request_invalid() -> None:
    with pytest.raises(ValidationError):
        SendEmailRequest(email="test")


def test_verify_email_request_valid_code() -> None:
    request = VerifyEmailRequest(email="test@example.com", code="123456")
    assert request.code == "123456"


@pytest.mark.parametrize(
    "invalid_code",
    [
        "12345",  # 5자리 (너무 짧음)
        "1234567",  # 7자리 (너무 김)
        "12345a",  # 숫자 아닌 문자 포함
        "",  #
    ],
)
def test_verify_email_request_invalid_code(invalid_code: str) -> None:
    with pytest.raises(ValidationError):
        VerifyEmailRequest(email="test@example.com", code=invalid_code)
