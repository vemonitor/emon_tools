from fastapi import APIRouter

from emon_tools.fastapi.api.routes import login
from emon_tools.fastapi.api.routes import users
from emon_tools.fastapi.api.routes import emon_fina
from emon_tools.fastapi.api.routes import emon_hosts
from emon_tools.fastapi.api.routes import category
from emon_tools.fastapi.api.routes import archive_file

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(emon_hosts.router)
api_router.include_router(category.router)
api_router.include_router(archive_file.router)
api_router.include_router(emon_fina.router)
