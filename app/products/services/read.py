from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3 import generate_presigned_download_url
from app.core.utils.pagination import CursorPage, CursorPageParams, paginate_by_cursor
from app.products.models import Product, ProductImage, Status
from app.products.schemas.read import ProductDetailResponse, ProductDisplay, ProductImageItem


async def list_products(db: AsyncSession, params: CursorPageParams) -> CursorPage[ProductDisplay]:
    stmt = select(Product).where(Product.status != Status.HIDDEN)
    products, next_cursor = await paginate_by_cursor(db, stmt, Product.id, params)
    product_ids = [product.id for product in products]
    thumbnail_result = await db.execute(
        select(ProductImage).where(ProductImage.product_id.in_(product_ids), ProductImage.order_number == 0)
    )
    thumbnails = {image.product_id: image.image_url for image in thumbnail_result.scalars().all()}

    items = [
        ProductDisplay(
            id=product.id,
            name=product.name,
            price=product.price,
            thumbnail=generate_presigned_download_url(thumbnails[product.id]) if product.id in thumbnails else None,
            brand=product.brand,
            category=product.category,
            status=product.status,
        )
        for product in products
    ]
    return CursorPage(items=items, next_cursor=next_cursor)


async def detail_product(db: AsyncSession, product_id: str) -> ProductDetailResponse:
    product = await db.get(Product, product_id)
    if product is None or product.status == Status.HIDDEN:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")
    result = await db.execute(
        select(ProductImage).where(ProductImage.product_id == product_id).order_by(ProductImage.order_number)
    )
    images = [
        ProductImageItem(key=image.image_url, url=generate_presigned_download_url(image.image_url))
        for image in result.scalars().all()
    ]
    return ProductDetailResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        size=product.size,
        price=product.price,
        brand=product.brand,
        category=product.category,
        status=product.status,
        images=images,
    )
