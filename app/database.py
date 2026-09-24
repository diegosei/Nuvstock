import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

sqlite_url = os.getenv("DATABASE_URL")

engine = create_engine(sqlite_url)


async def lifespan(app: FastAPI):

    SQLModel.metadata.create_all(engine)

    yield


def get_session():

    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
