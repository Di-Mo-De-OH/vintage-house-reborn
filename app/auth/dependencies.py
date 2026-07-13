import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.utils.redis import LogoutRedis
from app.core.redis import redis_client
from app.core.utils.security import decode_access_token

security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")

    if await redis_client.exists(LogoutRedis.blacklist(payload["jti"])):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그아웃된 토큰입니다.")

    return str(payload["user_id"])
