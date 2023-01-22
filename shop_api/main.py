from fastapi import FastAPI

from core.config import settings
from routers import categories, products

app = FastAPI(
    title=settings.PROJECT_TITLE,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)


@app.get("/", summary="Status")
async def index():
    return {"status": "OK"}


app.include_router(categories.router)
app.include_router(products.router)
