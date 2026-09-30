"""
Seed script: borra todo y crea datos de ejemplo para probar la API en Swagger/Postman.
"""

import random
from datetime import date

from sqlmodel import Session, SQLModel

from app.database import engine
from app.models.customers import Customer
from app.models.orders import Order, OrderItem, StatusEnum
from app.models.products import Product


def reset_database():
    print("Borrando y recreando tablas...")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def create_customers(session: Session) -> list[Customer]:
    simpsons = [
        {
            "name": "Homero",
            "last_name": "Simpson",
            "age": 39,
            "address": "742 Evergreen Terrace",
        },
        {
            "name": "Marge",
            "last_name": "Simpson",
            "age": 36,
            "address": "742 Evergreen Terrace",
        },
        {
            "name": "Bart",
            "last_name": "Simpson",
            "age": 10,
            "address": "742 Evergreen Terrace",
        },
        {
            "name": "Lisa",
            "last_name": "Simpson",
            "age": 8,
            "address": "742 Evergreen Terrace",
        },
        {
            "name": "Maggie",
            "last_name": "Simpson",
            "age": 1,
            "address": "742 Evergreen Terrace",
        },
    ]

    customers = []
    for data in simpsons:
        email = f"{data['name'].lower()}_{data['last_name'].lower()}@example.com"
        customer = Customer(
            name=data["name"],
            last_name=data["last_name"],
            age=data["age"],
            address=data["address"],
            email=email,
        )
        session.add(customer)
        customers.append(customer)

    session.commit()
    for customer in customers:
        session.refresh(customer)

    print(f"{len(customers)} customers creados.")
    return customers


def create_products(session: Session) -> list[Product]:
    catalog = [
        {"name": "Mechanical Keyboard", "price": 45000},
        {"name": "Gaming Mouse", "price": 22000},
        {"name": "24'' Monitor", "price": 180000},
        {"name": "Headphones", "price": 30000},
        {"name": "HD Webcam", "price": 25000},
        {"name": "Gaming Chair", "price": 250000},
        {"name": "Laptop Stand", "price": 15000},
        {"name": "XL Mousepad", "price": 8000},
    ]

    products = []
    for item in catalog:
        # Stock variado para poder probar fácil el caso de "sin stock" en Swagger.
        stock = random.choice([0, 2, 5, 10, 15, 20, 30])
        product = Product(name=item["name"], price=item["price"], stock=stock)
        session.add(product)
        products.append(product)

    session.commit()
    for product in products:
        session.refresh(product)

    print(f"{len(products)} products creados.")
    return products


def create_orders(session: Session, customers: list[Customer], products: list[Product]):
    available_products = [p for p in products if p.stock > 0]

    orders_plan = [
        # (customer, [(product, quantity), ...], status final)
        (
            customers[0],
            [(available_products[0], 1), (available_products[1], 2)],
            StatusEnum.PENDING,
        ),
        (customers[1], [(available_products[2], 1)], StatusEnum.PAID),
        (
            customers[2],
            [(available_products[3], 2), (available_products[4], 1)],
            StatusEnum.SHIPPED,
        ),
        (customers[3], [(available_products[5], 1)], StatusEnum.CANCELLED),
    ]

    created = 0
    for customer, items, final_status in orders_plan:
        order = Order(
            customer_id=customer.id, status=StatusEnum.PENDING, order_date=date.today()
        )

        for product, quantity in items:
            if quantity > product.stock:
                continue  # de última, por seguridad, no rompemos el seed
            order_item = OrderItem(
                product_id=product.id, quantity=quantity, price_unit=product.price
            )
            order.items.append(order_item)
            product.stock -= quantity
            session.add(product)

        session.add(order)
        session.commit()
        session.refresh(order)

        # Si el pedido "final" no es pending, lo llevamos ahí (simulando
        # el mismo camino de transiciones que ya validás en el endpoint)
        if final_status == StatusEnum.PAID:
            order.status = StatusEnum.PAID
        elif final_status == StatusEnum.SHIPPED:
            order.status = StatusEnum.PAID
            session.add(order)
            session.commit()
            order.status = StatusEnum.SHIPPED
        elif final_status == StatusEnum.CANCELLED:
            order.status = StatusEnum.CANCELLED
            for item in order.items:
                product = session.get(Product, item.product_id)
                product.stock += item.quantity
                session.add(product)

        session.add(order)
        session.commit()
        created += 1

    print(f"{created} orders creados (con distintos estados).")


def main():
    reset_database()
    with Session(engine) as session:
        customers = create_customers(session)
        products = create_products(session)
        create_orders(session, customers, products)

    print("\nSeed completo. Levantá el server y mirá /docs o Postman.")


if __name__ == "__main__":
    main()
