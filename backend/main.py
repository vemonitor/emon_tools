"""emon_tools/fastapi/main.py"""
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api.main import api_router
from backend.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate a unique identifier for a given API route.

    Args:
        route (APIRoute):
            The API route for which to generate the unique identifier.

    Returns:
        str:
            A unique identifier string composed of the route's
            first tag and name.
    """
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=3600,  # cache preflight requests for 1 hour
)

app.mount(
    '/static',
    StaticFiles(directory=settings.STATIC_BASE_PATH),
    name="static"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=5378,
        reload=True
    )
