from fastapi import FastAPI
from routers import categories, products

app = FastAPI(
    title="Shop API",
    description="A shop API",
    version="0.1.0"
)


@app.get("/", summary="Status")
async def index():
    return {"status": "OK"}


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(categories.router)
app.include_router(products.router)
