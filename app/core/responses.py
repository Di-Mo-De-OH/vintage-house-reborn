from typing import Any

SERVICE_UNAVAILABLE: dict[str, Any] = {
    "description": "일시적 서비스 장애 (Redis/DB/외부 API)",
    "content": {
        "application/json": {
            "example": {"detail": "일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요."}
        }
    },
}
