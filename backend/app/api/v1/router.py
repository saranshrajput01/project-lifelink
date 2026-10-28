"""
API v1 router — combines all endpoint routers into one.
"""

from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.family import router as family_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.predictions import router as predictions_router
from app.api.v1.endpoints.profile import router as profile_router
from app.api.v1.endpoints.reminders import router as reminders_router

api_router = APIRouter()

# Register all endpoint routers
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(documents_router)
api_router.include_router(reminders_router)
api_router.include_router(family_router)
api_router.include_router(predictions_router)
api_router.include_router(chat_router)
api_router.include_router(admin_router)
