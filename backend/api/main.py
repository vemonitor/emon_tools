"""
Main routes
"""
from fastapi import APIRouter

from backend.api.routes import (
    data_path,
    fina_data,
    login,
    users,
    emon_hosts,
    category,
    archive_file,
    dashboard
)

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(dashboard.router)
api_router.include_router(emon_hosts.router)
api_router.include_router(category.router)
api_router.include_router(data_path.router)
api_router.include_router(archive_file.router)
api_router.include_router(fina_data.router)
