from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_admin_user
from app.auth.models import User
from app.core.database import DbSession
from app.core.s3 import PresignedUrlRequest, PresignedUrlResponse, create_presigned_upload_url
from app.products.schemas.create import ProductCreateRequest, ProductCreateResponse
from app.products.services.create import create_product

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.put("/presigned-url", status_code=status.HTTP_200_OK, response_model=PresignedUrlResponse)
async def create_products_presigned_url(
    request: PresignedUrlRequest,
    admin: User = Depends(get_admin_user),
) -> PresignedUrlResponse:
    return create_presigned_upload_url(request, prefix="products")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProductCreateResponse)
async def create_products_post(
    db: DbSession,
    request: ProductCreateRequest,
    admin: User = Depends(get_admin_user),
) -> ProductCreateResponse:
    return await create_product(db, request)
