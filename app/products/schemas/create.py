from pydantic import BaseModel, Field

from app.products.models import Category


class ProductCreateRequest(BaseModel):
    name: str = Field(examples=["빈티지 데님 자켓"])
    description: str = Field(examples=["1990년대 빈티지 데님 자켓입니다."])
    size: str = Field(examples=["M"])
    price: int = Field(examples=[89000])
    brand: str | None = Field(default=None, examples=["Levi's"])
    category: Category = Field(examples=[Category.OUTER])
    image_keys: list[str] = Field(examples=[["products/01K8X...abc.jpg"]])


class ProductCreateResponse(BaseModel):
    id: str = Field(examples=["01JB3X8Z9Q0K4C7D2E5F6G7H8J"])
    name: str = Field(examples=["빈티지 데님 자켓"])
    description: str = Field(examples=["1990년대 빈티지 데님 자켓입니다."])
    size: str = Field(examples=["M"])
    price: int = Field(examples=[89000])
    brand: str | None = Field(default=None, examples=["Levi's"])
    category: Category
    image_keys: list[str] = Field(examples=[["products/01K8X...abc.jpg"]])
