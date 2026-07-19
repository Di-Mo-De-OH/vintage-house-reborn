from typing import Any

from fastapi import status

PRODUCTS_ADMIN_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "인증 토큰 없음, 만료 또는 로그아웃된 토큰",
        "content": {"application/json": {"example": {"detail": "유효하지 않은 토큰입니다."}}},
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "관리자가 아님",
        "content": {"application/json": {"example": {"detail": "관리자만 접근 가능합니다."}}},
    },
}
