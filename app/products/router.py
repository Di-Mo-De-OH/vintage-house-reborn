from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from app.auth.dependencies import get_admin_user
from app.auth.models import User
from app.core.s3 import PresignedUrlRequest, PresignedUrlResponse, create_presigned_upload_url

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

optional_bearer = HTTPBearer(auto_error=False)


@router.put("/presigned-url", status_code=status.HTTP_200_OK, response_model=PresignedUrlResponse)
async def create_products_presigned_url(
    request: PresignedUrlRequest,
    admin: User = Depends(get_admin_user),
) -> PresignedUrlResponse:
    return create_presigned_upload_url(request, prefix="products")
