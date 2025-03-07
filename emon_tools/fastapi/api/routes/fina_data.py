import math
import numpy as np
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel, OutputType
from emon_tools.emon_fina.emon_fina import FinaData
from emon_tools.emon_api.api_utils import Utils as Ut
from emon_tools.fastapi.api.deps import CurrentUser, SessionDep
from emon_tools.fastapi.crud import get_file_item, get_files_from_data_path, get_data_path, register_files
from emon_tools.fastapi.models.base import ResponseModelBase
from emon_tools.fastapi.models.db import DataPath
from emon_tools.fastapi.utils.emon_fina_helper import EmonFinaHelper
from emon_tools.fastapi.models.emon_fina import EmonFinaDataArgsModel, FilePathModel, FileSourceModel
from emon_tools.fastapi.models.emon_fina import GetFinaDataModel
from emon_tools.fastapi.models.emon_fina import EmonFinaArgsModel
from emon_tools.fastapi.utils.errors_parser import parse_integrity_error
from emon_tools.fastapi.utils.errors_parser import parse_pydantic_errors
from emon_tools.fastapi.utils.files import FilesHelper

router = APIRouter(prefix="/fina_data", tags=["fina_data"])


@router.get("/")
async def read_root() -> dict:
    """Dummy root endpoint."""
    return {"success": True, "data": "Welcome to your blog!"}


@router.get("/is-valid-data-path/{path_id}/", response_model=ResponseModelBase)
async def is_valid_source(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    path_id: int
) -> dict:
    """Test if if is valid source directory."""
    try:
        item = get_data_path(
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
    except (IntegrityError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg=(
                "Database integrity error: "
                "Possibly duplicate entry or invalid reference."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            from_error="IntegrityError",
            errors=parse_integrity_error(ex),
        )
    except (ValidationError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg="Database integrity error: Validation Error.",
            from_error="ValidationError",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=parse_pydantic_errors(ex),
        )
    except (ValueError, TypeError, IOError) as ex:
        return ResponseModelBase(
            success=False,
            error=str(ex)
        )
    except Exception as ex:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex


@router.get("/files/{path_id}/", response_model=ResponseModelBase)
async def get_files_list(
    session: SessionDep,
    current_user: CurrentUser,
    path_id: int
) -> ResponseModelBase:
    """Get phpfina files list from source."""
    try:
        files = get_files_from_data_path(
            session=session,
            current_user=current_user,
            item_id=path_id
        )
        output_files = EmonFinaHelper.append_fina_data(
            files=files
        )
        nb_added = register_files(
            session=session,
            current_user=current_user,
            files=output_files
        )
        if output_files is not None:
            return ResponseModelBase(
                success=True,
                data={
                    'path_id': output_files.get('file_path').id,
                    'files': output_files.get('files')
                }
            )
        return ResponseModelBase(
                success=True,
                data=None
            )
    except (IntegrityError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg=(
                "Database integrity error: "
                "Possibly duplicate entry or invalid reference."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            from_error="IntegrityError",
            errors=parse_integrity_error(ex),
        )
    except (ValidationError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg="Database integrity error: Validation Error.",
            from_error="ValidationError",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=parse_pydantic_errors(ex),
        )
    except (ValueError, TypeError, IOError) as ex:
        return ResponseModelBase(
            success=False,
            error=str(ex)
        )
    except Exception as ex:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex


@router.get("/meta/{file_id}/", response_model=ResponseModelBase)
async def get_file_meta(
    session: SessionDep,
    current_user: CurrentUser,
    file_id: int
) -> ResponseModelBase:
    """Get phpfina files list from source."""
    try:
        EmonFinaDataArgsModel(
            file_id=file_id
        )
        file_item = get_file_item(
            session=session,
            current_user=current_user,
            item_id=file_id
        )
        if file_item is not None:
            fina = FinaData(
                file_name=file_item.file_name,
                data_dir=file_item.datapath.path
            )
            return ResponseModelBase(
                success=True,
                data={
                    "file_id": file_id,
                    "datapath_id": file_item.datapath_id,
                    "emonhost_id": file_item.emonhost_id,
                    "meta": fina.meta.serialize()
                }
            )
    except (IntegrityError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg=(
                "Database integrity error: "
                "Possibly duplicate entry or invalid reference."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            from_error="IntegrityError",
            errors=parse_integrity_error(ex),
        )
    except (ValidationError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg="Database integrity error: Validation Error.",
            from_error="ValidationError",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=parse_pydantic_errors(ex),
        )
    except (ValueError, TypeError, IOError) as ex:
        return ResponseModelBase(
            success=False,
            error=str(ex)
        )
    except Exception as ex:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex


@router.get("/data/{file_id}/", response_model=ResponseModelBase)
async def get_file_data(
    session: SessionDep,
    current_user: CurrentUser,
    file_id: int,
    start: int = 0,
    interval: int = 0,
    window: int = 0
) -> dict:
    """Get phpfina files list from source."""
    try:
        GetFinaDataModel(
            file_id=file_id,
            start=start,
            interval=interval,
            window=window
        )
        file_item = get_file_item(
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
                return ResponseModelBase(
                    success=True,
                    data={
                        "file_id": file_id,
                        "datapath_id": file_item.datapath_id,
                        "emonhost_id": file_item.emonhost_id,
                        "data": datas.tolist()
                    }
                )
            return ResponseModelBase(
                success=True,
                data={
                    "file_id": file_id,
                    "datapath_id": file_item.datapath_id,
                    "emonhost_id": file_item.emonhost_id,
                    "data": []
                }
            )
    except (IntegrityError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg=(
                "Database integrity error: "
                "Possibly duplicate entry or invalid reference."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            from_error="IntegrityError",
            errors=parse_integrity_error(ex),
        )
    except (ValidationError) as ex:
        session.rollback()  # Ensure the session is rolled back
        return ResponseModelBase(
            success=False,
            msg="Database integrity error: Validation Error.",
            from_error="ValidationError",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=parse_pydantic_errors(ex),
        )
    except (ValueError, TypeError, IOError) as ex:
        return ResponseModelBase(
            success=False,
            error=str(ex)
        )
    except Exception as ex:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex
