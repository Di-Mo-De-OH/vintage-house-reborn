from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3 import delete_object, generate_presigned_download_url
from app.products.models import Product, ProductImage
from app.products.schemas.read import ProductDetailResponse, ProductImageItem
from app.products.schemas.update import ProductUpdateRequest


async def update(db: AsyncSession, request: ProductUpdateRequest, product_id: str) -> ProductDetailResponse:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")
    update_data = request.model_dump(exclude_unset=True, exclude={"image_keys"})
    for key, value in update_data.items():
        setattr(product, key, value)

    if request.image_keys is not None:
        old_image_result = await db.execute(select(ProductImage).where(ProductImage.product_id == product_id))
        product_images = old_image_result.scalars().all()
        for old_image in product_images:
            delete_object(old_image.image_url)
            await db.delete(old_image)

        for order_number, key in enumerate(request.image_keys):
            db.add(ProductImage(product_id=product_id, image_url=key, order_number=order_number))
    await db.commit()

    image_result = await db.execute(
        select(ProductImage).where(ProductImage.product_id == product_id).order_by(ProductImage.order_number)
    )
    images = [
        ProductImageItem(key=image.image_url, url=generate_presigned_download_url(image.image_url))
        for image in image_result.scalars().all()
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
