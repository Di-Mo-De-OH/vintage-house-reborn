import enum

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import BaseModel


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, enum.Enum):
    READY = "READY"  # 결제 생성 직후 초기 상태
    IN_PROGRESS = "IN_PROGRESS"  # 결제수단 인증 완료
    WAITING_FOR_DEPOSIT = "WAITING_FOR_DEPOSIT"  # 가상계좌 입금 대기
    DONE = "DONE"  # 승인 완료
    CANCELED = "CANCELED"  # 전체 취소
    PARTIAL_CANCELED = "PARTIAL_CANCELED"  # 부분 취소
    ABORTED = "ABORTED"  # 승인 실패
    EXPIRED = "EXPIRED"  # 30분 결제 유효시간 만료


class Order(BaseModel):
    __tablename__ = "orders"
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING
    )
    total_amount: Mapped[int] = mapped_column(Integer)


class OrderItem(BaseModel):
    __tablename__ = "order_items"
    order_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("products.id"), index=True
    )
    price_at_purchase: Mapped[int] = mapped_column(Integer)


class Payment(BaseModel):
    __tablename__ = "payments"

    order_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    toss_payment_key: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus))
    amount: Mapped[int] = mapped_column(Integer)
