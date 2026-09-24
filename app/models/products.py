from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    name: str
    price: int
    stock: int


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass
