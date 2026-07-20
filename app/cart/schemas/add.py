from pydantic import BaseModel, Field


class CartAddProductResponse(BaseModel):
    name: str = Field(examples=["장바구니에 등록된 상품명"])
