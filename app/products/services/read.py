from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3 import generate_presigned_download_url
from app.core.utils.pagination import CursorPage, CursorPageParams, paginate_by_cursor
from app.products.models import Product, ProductImage, Status
from app.products.schemas.read import ProductDisplay


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
