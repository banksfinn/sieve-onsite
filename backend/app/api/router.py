from fastapi import APIRouter

from app.api.routes.authentication.google import router as google_auth_router
from app.api.routes.user import router as user_router

api_router = APIRouter()

api_router.include_router(user_router, tags=["user"], prefix="/user")
api_router.include_router(google_auth_router, tags=["authentication"], prefix="/authentication/google")
