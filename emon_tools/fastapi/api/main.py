from fastapi import APIRouter

from emon_tools.fastapi.api.routes import emon_fina
from emon_tools.fastapi.core.config import settings

api_router = APIRouter()
api_router.include_router(emon_fina.router)
