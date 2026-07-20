from fastapi import HTTPException, status
from redis import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.schemas.read import CartItem, CartResponse
from app.cart.utils.redis import CartRedis
from app.core.redis import redis_client
from app.core.s3 import generate_presigned_download_url
from app.products.models import Product, ProductImage, Status


async def get_cart_item(db: AsyncSession, user_id: str) -> CartResponse:
    cart_key = CartRedis.key(user_id)
    try:
        product_ids = await redis_client.smembers(cart_key)
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
    if not product_ids:
        return CartResponse(items=[], total_price=0)

    result = await db.execute(select(Product).where(Product.id.in_(product_ids), Product.status == Status.ON_SALE))
    products = result.scalars().all()
    if not products:
        return CartResponse(items=[], total_price=0)

    product_ids_found = [product.id for product in products]
    thumbnail_result = await db.execute(
        select(ProductImage).where(ProductImage.product_id.in_(product_ids_found), ProductImage.order_number == 0)
    )
    thumbnails = {image.product_id: image.image_url for image in thumbnail_result.scalars().all()}
    total_price = sum(product.price for product in products)

    items = [
        CartItem(
            product_id=product.id,
            name=product.name,
            price=product.price,
            thumbnail=generate_presigned_download_url(thumbnails[product.id]) if product.id in thumbnails else None,
        )
        for product in products
    ]
    return CartResponse(items=items, total_price=total_price)
