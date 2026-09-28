from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    name: str
    price: int = Field(ge=0)
    stock: int = Field(ge=0)


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: str | None = None
    price: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
