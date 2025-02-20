from fastapi import APIRouter

from emon_tools.fastapi.api.routes import items
from emon_tools.fastapi.api.routes import login
from emon_tools.fastapi.api.routes import private
from emon_tools.fastapi.api.routes import users
from emon_tools.fastapi.api.routes import emon_fina
from emon_tools.fastapi.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(items.router)
api_router.include_router(emon_fina.router)
