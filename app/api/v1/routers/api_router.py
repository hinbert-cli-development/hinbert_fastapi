"""Central versioned router registry."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, products, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(dashboard.router)
