from fastapi import APIRouter, status

from app.auth.responses import SEND_EMAIL_RESPONSES, VERIFY_EMAIL_RESPONSES
from app.auth.schemas import SendEmailRequest, VerifyEmailRequest, VerifyEmailResponse
from app.auth.service.email import send_verification_email, verify_email
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
    responses=VERIFY_EMAIL_RESPONSES,
)
async def verify_email_router(request: VerifyEmailRequest, db: DbSession) -> VerifyEmailResponse:
    return await verify_email(db, request.email, request.code)
