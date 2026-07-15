from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.products.models import Product, ProductImage
from app.products.schemas.create import ProductCreateRequest, ProductCreateResponse


async def create_product(db: AsyncSession, request: ProductCreateRequest) -> ProductCreateResponse:
    product_id = str(ULID())

    product = Product(
        id=product_id,
        name=request.name,
        description=request.description,
        size=request.size,
        price=request.price,
        brand=request.brand,
        category=request.category,
    )
    db.add(product)

    for order_number, key in enumerate(request.image_keys):
        db.add(ProductImage(product_id=product_id, image_url=key, order_number=order_number))

    await db.commit()
    return ProductCreateResponse(
        id=product_id,
        name=product.name,
        description=product.description,
        size=product.size,
        price=product.price,
        brand=product.brand,
        category=product.category,
        image_keys=request.image_keys,
    )
