from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models.customers import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()


@router.post(
    "/customers",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
    tags=["customers"],
)
def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email isn't valid or already registered",
        )
    session.refresh(customer)
    return customer


# select -> construye consulta. exec -> ejecuta consulta
@router.get(
    "/customers",
    response_model=list[Customer],
    status_code=status.HTTP_200_OK,
    tags=["customers"],
)
def read_list_customer(session: SessionDep):
    customer_list = session.exec(select(Customer)).all()
    return customer_list


@router.get(
    "/customers/{customer_id}",
    response_model=Customer,
    status_code=status.HTTP_200_OK,
    tags=["customers"],
)
def read_customer_from_id(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    return customer


@router.put(
    "/customers/{customer_id}",
    response_model=Customer,
    status_code=status.HTTP_200_OK,
    tags=["customers"],
)
def update_customer(
    customer_id: int, customer_data: CustomerUpdate, session: SessionDep
):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    customer_data_dict = customer_data.model_dump(exclude_unset=True)
    customer.sqlmodel_update(customer_data_dict)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.delete(
    "/customers/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["customers"],
)
def delete_customer(customer_id: int, session: SessionDep):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )
    session.delete(customer)
    session.commit()
