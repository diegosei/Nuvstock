from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class CustomerBase(SQLModel):
    name: str
    last_name: str
    age: int
    address: str
    description: str | None = None
    email: EmailStr = Field(unique=True)


class Customer(CustomerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    name: str | None = None
    last_name: str | None = None
    age: int | None = None
    address: str | None = None
    email: EmailStr | None = None
