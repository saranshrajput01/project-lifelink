"""
API v1 router — combines all endpoint routers into one.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router

api_router = APIRouter()

# Register all endpoint routers
api_router.include_router(health_router)
api_router.include_router(auth_router)
