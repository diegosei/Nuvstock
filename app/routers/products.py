from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models.products import Product, ProductCreate, ProductUpdate

router = APIRouter()


@router.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    tags=["products"],
)
def create_product(product_data: ProductCreate, session: SessionDep):
    product = Product.model_validate(product_data.model_dump())
    if product.price < 0 or product.stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="price and stock can't be negative",
        )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get(
    "/products",
    response_model=list[Product],
    status_code=status.HTTP_200_OK,
    tags=["products"],
)
def read_list_product(session: SessionDep):
    products = session.exec(select(Product)).all()
    return products


@router.get(
    "/products/{product_id}",
    response_model=Product,
    status_code=status.HTTP_200_OK,
    tags=["products"],
)
def read_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        )
    return product


@router.patch(
    "/products/{product_id}",
    response_model=Product,
    status_code=status.HTTP_200_OK,
    tags=["products"],
)
def update_product(product_id: int, product_data: ProductUpdate, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        )
    product_data_dict = product_data.model_dump(exclude_unset=True)
    product.sqlmodel_update(product_data_dict)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["products"],
)
def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        )
    session.delete(product)
    session.commit()
