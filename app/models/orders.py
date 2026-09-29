from datetime import date
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class StatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


VALID_TRANSITIONS: dict[StatusEnum, set[StatusEnum]] = {
    StatusEnum.PENDING: {StatusEnum.PAID, StatusEnum.CANCELLED},
    StatusEnum.PAID: {StatusEnum.SHIPPED, StatusEnum.CANCELLED},
    StatusEnum.SHIPPED: set(),
    StatusEnum.CANCELLED: set(),
}


class OrderStatusUpdate(SQLModel):
    status: StatusEnum


class OrderItemBase(SQLModel):
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    price_unit: int


class OrderItem(OrderItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    order: "Order" = Relationship(back_populates="items")


class OrderBase(SQLModel):
    status: StatusEnum
    order_date: date


class Order(OrderBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    items: list["OrderItem"] = Relationship(back_populates="order")


class OrderRead(OrderBase):
    id: int
    customer_id: int
    items: list["OrderItem"]
    total: float


class OrderItemCreate(SQLModel):
    product_id: int
    quantity: int


class OrderCreate(SQLModel):
    customer_id: int
    items: list[OrderItemCreate]
