from pydantic import BaseModel, Field

from app.products.models import Category, Status


class ProductUpdateRequest(BaseModel):
    name: str | None = Field(default=None, examples=["빈티지 데님 자켓"])
    description: str | None = Field(default=None, examples=["1990년대 빈티지 데님 자켓입니다."])
    size: str | None = Field(default=None, examples=["M"])
    price: int | None = Field(default=None, examples=[89000])
    brand: str | None = Field(default=None, examples=["Levi's"])
    category: Category | None = Field(default=None, examples=[Category.OUTER])
    status: Status | None = Field(default=None, examples=[Status.SOLD_OUT])
    image_keys: list[str] | None = Field(default=None, examples=[["products/01K8X...abc.jpg"]])
