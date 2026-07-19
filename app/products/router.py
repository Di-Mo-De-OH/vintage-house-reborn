from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_admin_user
from app.auth.models import User
from app.core.database import DbSession
from app.core.s3 import PresignedUrlRequest, PresignedUrlResponse, create_presigned_upload_url
from app.core.utils.pagination import CursorPage, CursorPageParams
from app.products.schemas.create import ProductCreateRequest, ProductCreateResponse
from app.products.schemas.read import ProductDetailResponse, ProductDisplay
from app.products.services.create import create_product
from app.products.services.read import detail_product, list_products
from app.products.utils.responses import PRODUCT_NOT_FOUND_RESPONSES, PRODUCTS_ADMIN_RESPONSES

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.put(
    "/presigned-url",
    status_code=status.HTTP_200_OK,
    response_model=PresignedUrlResponse,
    responses=PRODUCTS_ADMIN_RESPONSES,
)
async def create_products_presigned_url(
    request: PresignedUrlRequest,
    admin: User = Depends(get_admin_user),
) -> PresignedUrlResponse:
    return create_presigned_upload_url(request, prefix="products")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductCreateResponse,
    responses=PRODUCTS_ADMIN_RESPONSES,
)
async def create_products_post(
    db: DbSession,
    request: ProductCreateRequest,
    admin: User = Depends(get_admin_user),
) -> ProductCreateResponse:
    return await create_product(db, request)


@router.get("", status_code=status.HTTP_200_OK, response_model=CursorPage[ProductDisplay])
async def get_products(
    db: DbSession,
    params: Annotated[CursorPageParams, Depends()],
) -> CursorPage[ProductDisplay]:
    return await list_products(db, params)


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductDetailResponse,
    responses=PRODUCT_NOT_FOUND_RESPONSES,
)
async def get_product(
    db: DbSession,
    product_id: str,
) -> ProductDetailResponse:
    return await detail_product(db, product_id)
