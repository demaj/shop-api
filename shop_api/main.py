from fastapi import FastAPI

from core.database import database
from routers import categories, products

app = FastAPI(title="Shop API", description="Shop API", version="0.1.0")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/", summary="Status")
async def index():
    return {"status": "OK"}


app.include_router(categories.router)
app.include_router(products.router)
