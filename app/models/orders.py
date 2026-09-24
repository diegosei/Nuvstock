from datetime import date
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class StatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class OrderItemBase(SQLModel):
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    price_unit: float


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


# create individual items order
class OrderItemCreate(SQLModel):
    product_id: int
    quantity: int


# create full order
class OrderCreate(SQLModel):
    customer_id: int
    items: list[OrderItemCreate]
