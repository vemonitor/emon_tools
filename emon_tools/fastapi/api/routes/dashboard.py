"""
DashBoard routes
"""
from fastapi import APIRouter
from emon_tools.fastapi.api.deps import CurrentUser, SessionDep
from emon_tools.fastapi.controllers.base import BaseController
from emon_tools.fastapi.controllers.dashboard import DashboardController
from emon_tools.fastapi.controllers.data_path import DataPathController
from emon_tools.fastapi.controllers.emon_host import EmonHostController
from emon_tools.fastapi.controllers.files import FilesController
from emon_tools.fastapi.models.base import (
    ResponseErrorBase
)
from emon_tools.fastapi.models.dashboard import (
    ModelsCountStats,
    RangeActivityType,
    UsersActivity
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
# pylint: disable=broad-exception-caught, unused-argument


@router.get(
    "/users/activity/",
    response_model=UsersActivity,
    responses={
        500: {
            "model": ResponseErrorBase
        }
    }
)
async def get_dash_users_stats(
    session: SessionDep,
    current_user: CurrentUser
) -> UsersActivity:
    """Get phpfina files list from source."""
    return DashboardController.get_dash_users_stats(
        session=session,
        current_user=current_user,
        time_range=RangeActivityType.MONTH
    )


@router.get(
    "/users/activity/current/",
    response_model=UsersActivity,
    responses={
        500: {
            "model": ResponseErrorBase
        }
    }
)
async def get_dash_current_user_stats(
    session: SessionDep,
    current_user: CurrentUser
) -> UsersActivity:
    """Get phpfina files list from source."""
    return DashboardController.get_dash_users_stats(
        session=session,
        current_user=current_user,
        time_range=RangeActivityType.MONTH,
        is_current=True
    )


@router.get(
    "/view/",
    response_model=ModelsCountStats,
    responses={
        500: {
            "model": ResponseErrorBase
        }
    }
)
async def get_dash_stats(
    session: SessionDep,
    current_user: CurrentUser
) -> ModelsCountStats:
    """Get phpfina files list from source."""
    try:
        return ModelsCountStats(
            nb_files=FilesController.count_files_by_types(
                session=session
            ),
            file_sizes=FilesController.sum_archive_file_sizes_by_types(
                session=session
            ),
            nb_paths=DataPathController.count_data_path(
                session=session
            ),
            nb_hosts=EmonHostController.count_emon_hosts(
                session=session
            )
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )
