from pydantic import BaseModel, Field

from app.products.models import Category, Status


class ProductDisplay(BaseModel):
    id: str = Field(examples=["01K8X...abc"])
    name: str = Field(examples=["상품명"])
    price: int = Field(examples=[10000])
    thumbnail: str | None = Field(default=None, examples=["https://..."])
    brand: str | None = Field(default=None, examples=["나이키"])
    category: Category = Field(examples=["TOP"])
    status: Status = Field(examples=["ON_SALE"])


class ProductDetailResponse(BaseModel):
    id: str = Field(examples=["01K8X...abc"])
    name: str = Field(examples=["상품명"])
    description: str = Field(examples=["제품 설명란"])
    price: int = Field(examples=[10000])
    size: str = Field(examples=["XL"])
    brand: str | None = Field(default=None, examples=["나이키"])
    category: Category = Field(examples=["TOP"])
    status: Status = Field(examples=["ON_SALE"])
    images: list[str] = Field(examples=[["https://...", "https://..."]])
