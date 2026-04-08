from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from logging_manager.logger import configure_logging
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from app.api.router import api_router as sieve_router
from app.config import settings
from app.models import all_models  # type: ignore # noqa: F401


def generate_unique_id(route: APIRoute):
    return f"{route.name}"


APP_TITLE = "sieve-onsite"

app = FastAPI(title=APP_TITLE, generate_unique_id_function=generate_unique_id)

# In deployed environments, restrict CORS to the frontend origin
# In local development, allow all origins for flexibility
cors_origins: list[str] = [settings.FRONTEND_URL] if settings.is_deployed else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_logging()

health_router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str


@health_router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(status="ok")


app.include_router(prefix="/api/gateway", router=sieve_router)
app.include_router(router=health_router)
