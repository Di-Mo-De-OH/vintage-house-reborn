from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3 import delete_object
from app.products.models import Product, ProductImage


async def delete(db: AsyncSession, product_id: str) -> None:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")

    result = await db.execute(select(ProductImage).where(ProductImage.product_id == product_id))
    for image in result.scalars().all():
        delete_object(image.image_url)
    await db.delete(product)
    await db.commit()
