from fastapi import HTTPException, status
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cart.schemas.add import CartAddProductResponse
from app.cart.utils.redis import CartRedis
from app.core.redis import redis_client
from app.products.models import Product, Status

TTL = 60 * 60 * 24 * 7


async def add(db: AsyncSession, product_id: str, user_id: str) -> CartAddProductResponse:
    product_result = await db.execute(select(Product).where(Product.id == product_id))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 상품을 찾을 수 없습니다.")
    if product.status != Status.ON_SALE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="구매할 수 없는 상품입니다.")

    cart_key = CartRedis.key(user_id)
    try:
        await redis_client.sadd(cart_key, product.id)
        await redis_client.expire(cart_key, TTL)
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="일시적으로 서비스를 이용할 수 없습니다. 잠시 후 다시 시도해주세요.",
        )
    return CartAddProductResponse(
        name=product.name,
    )
