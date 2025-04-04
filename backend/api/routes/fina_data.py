"""
Fina Data Routes
"""
import math
import numpy as np
from fastapi import APIRouter, HTTPException

from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel, OutputType
from emon_tools.emon_fina.emon_fina import FinaData
from backend.api.deps import CurrentUser, SessionDep
from backend.controllers.base import BaseController
from backend.models.base import ResponseModelBase
from backend.controllers.data_path import DataPathController
from backend.controllers.files import FilesController
from backend.controllers.fina_data import FinaDataController
from backend.models.fina_data import (
    FileDataPoints,
    PathFiles,
    SelectedFileMeta
)
from backend.models.emon_fina import EmonFinaDataArgsModel
from backend.models.emon_fina import GetFinaDataModel
from backend.utils.files import FilesHelper

router = APIRouter(prefix="/fina_data", tags=["fina_data"])
# pylint: disable=broad-exception-caught


@router.get(
    "/is-valid-data-path/{path_id}/",
    response_model=ResponseModelBase,
    responses=BaseController.get_error_responses()
)
async def is_valid_source(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    path_id: int
) -> dict:
    """Test if if is valid source directory."""
    try:
        item = DataPathController.get_data_path(
            session=session,
            current_user=current_user,
            item_id=path_id
        )
        if not item:
            raise HTTPException(
                status_code=404, detail="Item not found")
        if not current_user.is_superuser\
                and (item.owner_id != current_user.id):
            raise HTTPException(
                status_code=400, detail="Not enough permissions")
        return ResponseModelBase(
            success=FilesHelper.is_readable_path(item.path)
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/files/{path_id}/",
    response_model=PathFiles,
    responses=BaseController.get_error_responses()
)
async def get_files_list(
    session: SessionDep,
    current_user: CurrentUser,
    path_id: int
) -> PathFiles:
    """Get phpfina files list from source."""
    try:
        output_files, nb_added = FinaDataController.get_files_list(
            session=session,
            current_user=current_user,
            path_id=path_id
        )
        if output_files is not None:
            return PathFiles(
                success=True,
                path_id=output_files.get('file_path').id,
                nb_added=nb_added,
                files=output_files.get('files')
            )
        return PathFiles(
            success=False,
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/files/by/{host_slug}/",
    response_model=PathFiles,
    responses=BaseController.get_error_responses()
)
async def get_files_list_by_slug(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    host_slug: str
) -> PathFiles:
    """Test if if is valid source directory."""
    try:
        data_path = DataPathController.get_data_path_by_slug(
            session=session,
            current_user=current_user,
            slug=host_slug
        )
        output_files, nb_added = FinaDataController.get_files_list(
            session=session,
            current_user=current_user,
            path_id=data_path.id
        )
        if output_files is not None\
                and nb_added is not None:
            return PathFiles(
                success=True,
                path_id=output_files.get('file_path').id,
                nb_added=nb_added,
                files=output_files.get('files')
            )
        return PathFiles(
            success=False,
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/meta/{file_id}/",
    response_model=SelectedFileMeta,
    responses=BaseController.get_error_responses()
)
async def get_file_meta(
    session: SessionDep,
    current_user: CurrentUser,
    file_id: int
) -> SelectedFileMeta:
    """Get phpfina files list from source."""
    try:
        EmonFinaDataArgsModel(
            file_id=file_id
        )
        file_item = FilesController.get_file_item(
            session=session,
            current_user=current_user,
            item_id=file_id
        )
        if file_item is not None:
            fina = FinaData(
                file_name=file_item.file_name,
                data_dir=file_item.datapath.path
            )
            return SelectedFileMeta(
                success=True,
                file_id=file_id,
                datapath_id=file_item.datapath_id,
                emonhost_id=file_item.emonhost_id,
                meta=fina.meta.serialize()
            )
        return SelectedFileMeta(
            success=False,
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/data/{file_id}/",
    response_model=FileDataPoints,
    responses=BaseController.get_error_responses()
)
async def get_file_data(
    session: SessionDep,
    current_user: CurrentUser,
    file_id: int,
    start: int = 0,
    interval: int = 0,
    window: int = 0
) -> FileDataPoints:
    """Get phpfina files list from source."""
    try:
        GetFinaDataModel(
            file_id=file_id,
            start=start,
            interval=interval,
            window=window
        )
        file_item = FilesController.get_file_item(
            session=session,
            current_user=current_user,
            item_id=file_id
        )
        if file_item is not None:
            fina = FinaData(
                file_name=file_item.file_name,
                data_dir=file_item.datapath.path
            )
            if start <= 0:
                start = fina.meta.start_time
            if interval <= 0:
                interval = fina.meta.interval
            if window <= 0:
                window = 3600
            real_start = start
            real_window = window
            if start < fina.meta.start_time\
                    and start >= fina.meta.start_time - window:
                real_start = max(start, fina.meta.start_time)
                real_window = window - (fina.meta.start_time - start)

            if real_start > 0\
                    and real_window > 0\
                    and interval > 0\
                    and real_start < fina.meta.end_time:
                datas = fina.get_fina_values(
                    FinaByTimeParamsModel(
                        start_time=real_start,
                        time_window=real_window,
                        time_interval=interval,
                    )
                )
                if start < fina.meta.start_time:
                    nb_na = math.ceil(
                        (fina.meta.start_time - start) / interval)
                    nans = np.full((nb_na, datas.shape[1],), np.nan)
                    nans[:, 0] = np.arange(
                        start, fina.meta.start_time, interval)
                    datas = np.concatenate((nans, datas), axis=0)

                if start + window > fina.meta.end_time:
                    nb_na = math.ceil(
                        (start + window - fina.meta.end_time) / interval)
                    nans = np.full((nb_na, datas.shape[1],), np.nan)
                    nans[:, 0] = np.arange(
                        fina.meta.end_time + interval,
                        start + window + interval, interval)
                    datas = np.concatenate((datas, nans), axis=0)
                return FileDataPoints(
                    success=True,
                    file_id=file_id,
                    feed_id=file_item.feed_id or 0,
                    datapath_id=file_item.datapath_id or 0,
                    emonhost_id=file_item.emonhost_id or 0,
                    file_name=file_item.file_name,
                    name=file_item.name,
                    data=datas.tolist(),
                )
            return FileDataPoints(
                success=True,
                file_id=file_id,
                datapath_id=file_item.datapath_id or 0,
                emonhost_id=file_item.emonhost_id or 0,
            )
        return FileDataPoints(
            success=True,
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/stats/{file_id}/",
    response_model=FileDataPoints,
    responses=BaseController.get_error_responses()
)
async def get_file_stats(
    session: SessionDep,
    current_user: CurrentUser,
    file_id: int,
    start: int = 0,
    interval: int = 0,
    window: int = 0
) -> FileDataPoints:
    """Get phpfina files list from source."""
    try:
        GetFinaDataModel(
            file_id=file_id,
            start=start,
            interval=interval,
            window=window
        )
        file_item = FilesController.get_file_item(
            session=session,
            current_user=current_user,
            item_id=file_id
        )
        if file_item is not None:
            fina = FinaData(
                file_name=file_item.file_name,
                data_dir=file_item.datapath.path
            )
            if start <= 0:
                start = fina.meta.start_time
            if interval <= 0:
                interval = 3600 * 24
            if window <= 0:
                window = 0
            real_start = start
            real_window = window
            if start < fina.meta.start_time\
                    and start >= fina.meta.start_time - window:
                real_start = max(start, fina.meta.start_time)
                real_window = window - (fina.meta.start_time - start)

            if real_start > 0\
                    and real_window > 0\
                    and interval > 0\
                    and real_start < fina.meta.end_time:
                datas = fina.get_fina_values(
                    FinaByTimeParamsModel(
                        start_time=real_start,
                        time_window=real_window,
                        time_interval=interval,
                        output_type=OutputType.INTEGRITY
                    )
                )
                if start < fina.meta.start_time:
                    nb_na = math.ceil(
                        (fina.meta.start_time - start) / interval)
                    nans = np.full((nb_na, datas.shape[1],), np.nan)
                    nans[:, 0] = np.arange(
                        start, fina.meta.start_time, interval)
                    datas = np.concatenate((nans, datas), axis=0)

                if start + window > fina.meta.end_time:
                    nb_na = math.ceil(
                        (start + window - fina.meta.end_time) / interval)
                    nans = np.full((nb_na, datas.shape[1],), np.nan)
                    nans[:, 0] = np.arange(
                        fina.meta.end_time + interval,
                        start + window + interval, interval)
                    datas = np.concatenate((datas, nans), axis=0)
                return FileDataPoints(
                    success=True,
                    file_id=file_id,
                    feed_id=file_item.feed_id,
                    datapath_id=file_item.datapath_id,
                    emonhost_id=file_item.emonhost_id,
                    file_name=file_item.file_name,
                    name=file_item.name,
                    data=datas.tolist(),
                )
            return FileDataPoints(
                success=True,
                file_id=file_id,
                datapath_id=file_item.datapath_id,
                emonhost_id=file_item.emonhost_id,
            )
        return FileDataPoints(
            success=True,
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )
