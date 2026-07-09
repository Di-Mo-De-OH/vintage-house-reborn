from fastapi import APIRouter, status

from app.auth.models import User
from app.auth.schemas.email import SendEmailRequest, VerifyEmailRequest, VerifyEmailResponse
from app.auth.schemas.signup import SignUpRequest, SignUpResponse
from app.auth.services.email import send_verification_email, verify_email
from app.auth.services.signup import signup
from app.auth.utils.responses import SEND_EMAIL_RESPONSES, SIGNUP_RESPONSES, VERIFY_EMAIL_RESPONSES
from app.core.database import DbSession

router = APIRouter(prefix="/auth", tags=["auth"])


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
async def verify_email_router(request: VerifyEmailRequest, db: DbSession) -> VerifyEmailResponse:
    return await verify_email(db, request.email, request.code)


@router.post(
    "/signup",
    response_model=SignUpResponse,
    status_code=status.HTTP_201_CREATED,
    responses=SIGNUP_RESPONSES,
)
async def signup_router(request: SignUpRequest, db: DbSession) -> User:
    return await signup(db, request)
