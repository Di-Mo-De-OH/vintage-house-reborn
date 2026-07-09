from typing import Any

from fastapi import status

from app.core.responses import SERVICE_UNAVAILABLE

SEND_EMAIL_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_429_TOO_MANY_REQUESTS: {
        "description": "재발송 쿨다운 중",
        "content": {"application/json": {"example": {"detail": "잠시 후 다시 시도해주세요."}}},
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: SERVICE_UNAVAILABLE,
}

VERIFY_EMAIL_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {
        "description": "인증 코드 불일치 또는 만료",
        "content": {"application/json": {"example": {"detail": "입력해 주신 코드가 다릅니다."}}},
    },
    status.HTTP_409_CONFLICT: {
        "description": "이미 가입된 이메일",
        "content": {"application/json": {"example": {"detail": "이미 가입된 이메일 입니다."}}},
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: SERVICE_UNAVAILABLE,
}

SIGNUP_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {
        "description": "이메일 인증 토큰 없음 또는 만료",
        "content": {"application/json": {"example": {"detail": "이메일 인증이 필요합니다."}}},
    },
    status.HTTP_409_CONFLICT: {
        "description": "이미 사용 중인 닉네임 또는 이메일",
        "content": {"application/json": {"example": {"detail": "이미 사용 중인 닉네임 입니다."}}},
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: SERVICE_UNAVAILABLE,
}
