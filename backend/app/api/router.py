from fastapi import APIRouter

from app.api.routes.authentication.google import router as google_auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.slack import router as slack_router
from app.api.routes.tag import router as tag_router
from app.api.routes.todo import router as todo_router
from app.api.routes.user import router as user_router

api_router = APIRouter()


api_router.include_router(todo_router, tags=["todo"], prefix="/todo")
api_router.include_router(tag_router, tags=["tag"], prefix="/tag")
api_router.include_router(user_router, tags=["user"], prefix="/user")
api_router.include_router(chat_router, tags=["chat"], prefix="/chat")
api_router.include_router(slack_router, tags=["slack"], prefix="/slack")
api_router.include_router(google_auth_router, tags=["authentication"], prefix="/authentication/google")
