from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.authentication.google import router as google_auth_router
from app.api.routes.clip import router as clip_router
from app.api.routes.dataset import router as dataset_router
from app.api.routes.dataset_assignment import router as dataset_assignment_router
from app.api.routes.delivery import router as delivery_router
from app.api.routes.user import router as user_router
from app.api.routes.video import router as video_router

api_router = APIRouter()

api_router.include_router(user_router, tags=["user"], prefix="/user")
api_router.include_router(dataset_router, tags=["dataset"], prefix="/dataset")
api_router.include_router(dataset_assignment_router, tags=["dataset_assignment"], prefix="/dataset-assignment")
api_router.include_router(video_router, tags=["video"], prefix="/video")
api_router.include_router(clip_router, tags=["clip"], prefix="/clip")
api_router.include_router(delivery_router, tags=["delivery"], prefix="/delivery")
api_router.include_router(admin_router, tags=["admin"], prefix="/admin")
api_router.include_router(google_auth_router, tags=["authentication"], prefix="/authentication/google")
