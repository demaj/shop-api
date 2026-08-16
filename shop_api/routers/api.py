from fastapi import APIRouter

from core.config import get_settings
from routers import auth, categories, products, users

api_router = APIRouter(prefix=get_settings().API_V1_STR)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.read_router)
api_router.include_router(categories.write_router)
api_router.include_router(products.read_router)
api_router.include_router(products.write_router)
