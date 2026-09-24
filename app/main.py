from fastapi import FastAPI
from fastapi_health import health

from app.database import lifespan

from .routers import customers

app = FastAPI(lifespan=lifespan)
app.include_router(customers.router)


@app.get("/")
def read_root():
    return {"message": "ok"}


def is_database_online():
    return True


app.add_api_route("/health", health([is_database_online]))
