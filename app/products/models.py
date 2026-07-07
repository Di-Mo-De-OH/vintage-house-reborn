import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class Category(str, enum.Enum):
    OUTER = "OUTER"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    SHOES = "SHOES"
    ACCESSORY = "ACCESSORY"


class Status(str, enum.Enum):
    ON_SALE = "ON_SALE"
    SOLD_OUT = "SOLD_OUT"
    HIDDEN = "HIDDEN"


class Product(BaseModel):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    size: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column(Integer)
    brand: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[Category] = mapped_column(Enum(Category))
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.ON_SALE)


class ProductImage(BaseModel):
    __tablename__ = "product_images"
    product_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    image_url: Mapped[str] = mapped_column(Text)
    order_number: Mapped[int] = mapped_column(Integer, default=0)
