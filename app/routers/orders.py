from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.database import SessionDep
from app.models.customers import Customer
from app.models.orders import (
    VALID_TRANSITIONS,
    Order,
    OrderCreate,
    OrderItem,
    OrderRead,
    OrderStatusUpdate,
    StatusEnum,
)
from app.models.products import Product

router = APIRouter()


# OrderCreate: customer_id / items: list[OrderItemCreate]
# OrderItemCreate: product_id / quantity
@router.post(
    "/orders",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    tags=["orders"],
)
def creater_order(order_data: OrderCreate, session: SessionDep):
    customer = session.get(Customer, order_data.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="customer not found"
        )

    order = Order(
        customer_id=customer.id,
        status=StatusEnum.PENDING,
        order_date=datetime.today(),  # noqa: DTZ002
    )

    for item in order_data.items:
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"product {item.product_id} not found",
            )
        if item.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"not enough stock for product {item.product_id}",
            )

        order_item = OrderItem(
            product_id=item.product_id, quantity=item.quantity, price_unit=product.price
        )

    order.items.append(order_item)
    product.stock -= item.quantity
    session.add(product)

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.get(
    "/orders/{order_id}",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
    tags=["orders"],
)
def read_order(order_id: int, session: SessionDep):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="order not found"
        )

    total = sum(item.quantity * item.price_unit for item in order.items)

    order_read = OrderRead(
        status=order.status,
        order_date=order.order_date,
        id=order.id,
        customer_id=order.customer_id,
        items=order.items,
        total=total,
    )

    return order_read


@router.put(
    "/orders/{order_id}",
    response_model=Order,
    status_code=status.HTTP_200_OK,
    tags=["orders"],
)
def update_order(order_id: int, status_data: OrderStatusUpdate, session: SessionDep):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="order not found"
        )

    new_status = status_data.status
    if new_status not in VALID_TRANSITIONS[order.status]:
        raise HTTPException(
            400, detail=f"cannot go from {order.status} to {new_status}"
        )

    order.status = new_status

    if new_status == StatusEnum.CANCELLED:
        for item in order.items:
            product = session.get(Product, item.product_id)
            product.stock += item.quantity
            session.add(product)

    session.add(order)
    session.commit()
    session.refresh(order)
    return order
