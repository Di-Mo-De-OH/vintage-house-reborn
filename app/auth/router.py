from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.dependencies import get_user
from app.auth.models import User
from app.auth.schemas.email import SendEmailRequest, VerifyEmailRequest, VerifyEmailResponse
from app.auth.schemas.login_logout import LoginRequest, LoginResponse
from app.auth.schemas.me import MeResponse, MeUpdateRequest
from app.auth.schemas.signup import SignUpRequest, SignUpResponse
from app.auth.services.email import send_verification_email, verify_email
from app.auth.services.login_logout import login, logout
from app.auth.services.me import delete, update
from app.auth.services.refresh import refresh
from app.auth.services.signup import signup
from app.auth.utils.responses import (
    LOGIN_RESPONSES,
    LOGOUT_RESPONSES,
    ME_RESPONSES,
    REFRESH_RESPONSES,
    SEND_EMAIL_RESPONSES,
    SIGNUP_RESPONSES,
    VERIFY_EMAIL_RESPONSES,
)
from app.core.config import settings
from app.core.database import DbSession

router = APIRouter(prefix="/auth", tags=["auth"])

optional_bearer = HTTPBearer(auto_error=False)


@router.post(
    "/send-email",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=SEND_EMAIL_RESPONSES,
)
async def send_email_router(request: SendEmailRequest) -> None:
    await send_verification_email(request.email)


@router.post(
    "/verify-email",
    response_model=VerifyEmailResponse,
    status_code=status.HTTP_200_OK,
    responses=VERIFY_EMAIL_RESPONSES,
)
async def verify_email_router(db: DbSession, request: VerifyEmailRequest) -> VerifyEmailResponse:
    return await verify_email(db, request.email, request.code)


@router.post(
    "/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
    responses=SIGNUP_RESPONSES,
)
async def signup_router(db: DbSession, request: SignUpRequest) -> User:
    return await signup(db, request)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK, responses=LOGIN_RESPONSES)
async def login_router(db: DbSession, request: LoginRequest, response: Response) -> LoginResponse:
    login_response, refresh_token = await login(db, request)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    return login_response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, responses=LOGOUT_RESPONSES)
async def logout_router(
    db: DbSession,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer)] = None,
) -> None:
    access_token = credentials.credentials if credentials else None
    await logout(db, refresh_token, access_token)
    response.delete_cookie("refresh_token")


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    responses=REFRESH_RESPONSES,
)
async def refresh_router(db: DbSession, refresh_token: Annotated[str | None, Cookie()] = None) -> LoginResponse:
    return await refresh(db, refresh_token)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=MeResponse, responses=ME_RESPONSES)
async def get_me(user: User = Depends(get_user)) -> User:
    return user


@router.patch("/me", status_code=status.HTTP_200_OK, response_model=MeResponse, responses=ME_RESPONSES)
async def update_me(db: DbSession, request: MeUpdateRequest, user: User = Depends(get_user)) -> User:
    return await update(db, request, user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, responses=ME_RESPONSES)
async def delete_me(db: DbSession, user: User = Depends(get_user)) -> None:
    return await delete(db, user)
