import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

database_url = os.getenv("DATABASE_URL")

connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(database_url, connect_args=connect_args)


async def lifespan(app: FastAPI):

    SQLModel.metadata.create_all(engine)

    yield


def get_session():

    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
