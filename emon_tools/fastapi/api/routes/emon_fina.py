"""emon_fina fastapi api routes"""
import math
import numpy as np
from fastapi import APIRouter
from pydantic import ValidationError
from emon_tools.emon_fina.emon_fina import FinaData, FinaStats, StatsType
from emon_tools.fastapi.utils.emon_fina import EmonFinaHelper
from emon_tools.fastapi.models.emon_fina import FileSourceModel
from emon_tools.fastapi.models.emon_fina import GetFinaDataModel
from emon_tools.fastapi.models.emon_fina import EmonFinaArgsModel

router = APIRouter(prefix="/emon_fina", tags=["emon_fina"])


@router.get("/")
async def read_root() -> dict:
    """Dummy root endpoint."""
    return {"success": True, "data": "Welcome to your blog!"}


@router.get("/files/{source}")
async def get_files_list(source: str) -> dict:
    """Get phpfina files list from source."""
    try:
        FileSourceModel.model_validate({
            'source': source,
        })
        files = EmonFinaHelper.scan_fina_dir(
            source=source
        )
    except (ValidationError, ValueError, TypeError, IOError) as ex:
        return {"success": False, "error": str(ex)}

    if len(files.get('files')) > 0:
        data_dir = EmonFinaHelper.get_files_source(
            source=source
        )
        result = []
        for fina_dat in files.get('files'):
            try:
                feed_id = int(fina_dat.split('.')[0])
                fina = FinaData(
                    feed_id=feed_id,
                    data_dir=data_dir
                )
                result.append({
                    "feed_id": feed_id,
                    "name": fina_dat,
                    "meta": fina.meta.serialize()
                })
            except (ValueError, TypeError) as ex:
                result.append({
                    "feed_id": feed_id,
                    "name": fina_dat,
                    "meta": {},
                    "error": str(ex)
                })
        files['files'] = result
        return files


@router.get("/meta/{source}/{feed_id}")
async def get_file_meta(
    source: str,
    feed_id: int
) -> dict:
    """Get phpfina files list from source."""
    try:
        EmonFinaArgsModel(
            source=source,
            feed_id=feed_id
        )
        fina = FinaData(
            feed_id=feed_id,
            data_dir=EmonFinaHelper.get_files_source(
                source=source
            )
        )
        return {
            "success": True,
            "feed_id": feed_id,
            "data": fina.meta.serialize()
        }
    except (ValidationError, ValueError, TypeError) as ex:
        return {"success": False, "error": str(ex)}


@router.get("/data/{source}/{feed_id}")
async def get_file_data(
    source: str,
    feed_id: int,
    start: int = 0,
    interval: int = 0,
    window: int = 0
) -> dict:
    """Get phpfina files list from source."""
    try:
        GetFinaDataModel(
            source=source,
            feed_id=feed_id,
            start=start,
            interval=interval,
            window=window
        )
        fina = FinaData(
            feed_id=feed_id,
            data_dir=EmonFinaHelper.get_files_source(
                source=source
            )
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
            datas = fina.get_fina_time_series(
                start=real_start,
                step=interval,
                window=real_window
            )
            datas[:, 1] = np.around(datas[:, 1], 3)
            if start < fina.meta.start_time:
                nb_na = math.ceil((fina.meta.start_time - start) / interval)
                nans = np.full((nb_na, 2,), np.nan)
                nans[:, 0] = np.arange(start, fina.meta.start_time, interval)
                datas = np.concatenate((nans, datas), axis=0)

            if start + window > fina.meta.end_time:
                nb_na = math.ceil(
                    (start + window - fina.meta.end_time) / interval)
                nans = np.full((nb_na, 2,), np.nan)
                nans[:, 0] = np.arange(
                    fina.meta.end_time + interval,
                    start + window + interval, interval)
                datas = np.concatenate((datas, nans), axis=0)
            return {
                "success": True,
                "feed_id": feed_id,
                "data": datas.tolist()
            }
        return {
                "success": True,
                "feed_id": feed_id,
                "data": []
            }
    except (ValidationError, ValueError, TypeError) as ex:
        return {"success": False, "error": str(ex)}


@router.get("/stats/{source}/{feed_id}")
async def get_file_stats(
    source: str,
    feed_id: int,
    start: int = 0,
    interval: int = 0,
    window: int = 0
) -> dict:
    """Get phpfina files list from source."""
    try:
        GetFinaDataModel(
            source=source,
            feed_id=feed_id,
            start=start,
            interval=interval,
            window=window
        )
        fina = FinaStats(
            feed_id=feed_id,
            data_dir=EmonFinaHelper.get_files_source(
                source=source
            )
        )
        if start <= 0:
            start = fina.meta.start_time
        if interval <= 0:
            interval = fina.meta.interval
        if window <= 0:
            window = 3600 * 24
        datas = fina.get_stats(
            start_time=start,
            steps_window=window,
            max_size=3600 * 24 * 8900,
            stats_type=StatsType.INTEGRITY
        )
        return {
            "success": True,
            "feed_id": feed_id,
            "data": datas
        }
    except (ValidationError, ValueError, TypeError) as ex:
        return {"success": False, "error": str(ex)}
