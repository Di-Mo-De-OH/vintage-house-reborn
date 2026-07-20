from pydantic import BaseModel, Field


class CartItem(BaseModel):
    product_id: str = Field(examples=["01K8X...abc"])
    name: str = Field(examples=["상품명"])
    price: int = Field(examples=[89000])
    thumbnail: str | None = Field(default=None, examples=["https://..."])


class CartResponse(BaseModel):
    items: list[CartItem] = Field(examples=[[]])
    total_price: int = Field(examples=[89000])
