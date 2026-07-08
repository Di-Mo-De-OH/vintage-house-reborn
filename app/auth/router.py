from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import SendEmailRequest, VerifyEmailRequest, VerifyEmailResponse
from app.auth.service.email import send_verification_email, verify_email
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-email", status_code=status.HTTP_204_NO_CONTENT)
async def send_email_router(request: SendEmailRequest) -> None:
    await send_verification_email(request.email)


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email_router(
    request: VerifyEmailRequest, db: AsyncSession = Depends(get_db)
) -> VerifyEmailResponse:
    return await verify_email(db, request.email, request.code)
