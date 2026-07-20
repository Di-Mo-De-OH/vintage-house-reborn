from typing import Any

from fastapi import status

from app.core.responses import SERVICE_UNAVAILABLE

CART_AUTH_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "인증 토큰 없음, 만료 또는 로그아웃된 토큰",
        "content": {"application/json": {"example": {"detail": "유효하지 않은 토큰입니다."}}},
    },
    status.HTTP_503_SERVICE_UNAVAILABLE: SERVICE_UNAVAILABLE,
}

CART_ADD_RESPONSES: dict[int | str, dict[str, Any]] = {
    **CART_AUTH_RESPONSES,
    status.HTTP_400_BAD_REQUEST: {
        "description": "구매할 수 없는 상품 (품절/숨김)",
        "content": {"application/json": {"example": {"detail": "구매할 수 없는 상품입니다."}}},
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "상품이 존재하지 않음",
        "content": {"application/json": {"example": {"detail": "해당 상품을 찾을 수 없습니다."}}},
    },
}
