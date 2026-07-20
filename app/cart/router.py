from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user_id
from app.cart.schemas.add import CartAddProductResponse
from app.cart.schemas.read import CartResponse
from app.cart.services.add import add
from app.cart.services.read import get_cart_item
from app.core.database import DbSession

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/{product_id}", status_code=status.HTTP_201_CREATED, response_model=CartAddProductResponse)
async def add_cart_router(
    db: DbSession, product_id: str, user_id: str = Depends(get_current_user_id)
) -> CartAddProductResponse:
    return await add(db, product_id, user_id)


@router.get("", status_code=status.HTTP_200_OK, response_model=CartResponse)
async def get_cart_router(db: DbSession, user_id: str = Depends(get_current_user_id)) -> CartResponse:
    return await get_cart_item(db, user_id)
