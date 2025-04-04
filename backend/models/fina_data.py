"""
FinaData Models
"""
from typing import Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel


class ResponseSuccess(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool
    data: Any


class MetaDict(TypedDict):
    """
    File Meta Dict Type
    """
    start_time: int
    end_time: int
    interval: int
    npoints: int
    size: int


class FileDataDict(TypedDict):
    """
    File Meta Dict Type
    """
    file_id: int
    name: str
    slug: str
    feed_id: int
    emonhost_id: Optional[int]


class PathFileItem(TypedDict):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    file_name: str
    name: str
    meta: MetaDict
    file_db: FileDataDict


class PathFiles(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool
    path_id: int = 0
    nb_added: int = 0
    files: list[Optional[PathFileItem]] = []


class SelectedFileMeta(BaseModel):
    """
    File Meta Dict Type
    """
    success: bool
    file_id: int = 0
    datapath_id: int = 0
    emonhost_id: int = 0
    meta: MetaDict | None = None


class FileDataPoints(BaseModel):
    """
    File Meta Dict Type
    """
    success: bool
    file_id: int = 0
    feed_id: int = 0
    datapath_id: int = 0
    emonhost_id: int = 0
    file_name: str = ""
    name: str = ""
    data: list[list[Any]] = []
