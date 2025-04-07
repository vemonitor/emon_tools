"""Emon Api Models"""
from typing import Any, Optional, Union
from typing_extensions import TypedDict
from typing_extensions import Annotated
from pydantic import BaseModel, Field

from backend.models.fina_data import FileDataDict, MetaDict


class ApiFeedItem(TypedDict):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    id: int
    name: str
    tag: str
    public: str
    engine: str
    unit: str
    time: Optional[int]
    value: Optional[Union[float, int]]
    start_time: int
    end_time: int
    interval: int
    npoints: int
    size: int


class ApiFeeds(TypedDict):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool
    message: Optional[list[ApiFeedItem]]


class EmonFeedItem(TypedDict):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    id: int
    userid: int
    name: str
    tag: str
    public: bool
    engine: str
    unit: str
    meta: MetaDict
    files: list[Optional[FileDataDict]] = []


class EmonFeeds(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool
    host_id: int = 0
    nb_feeds: int = 0
    feeds: list[Optional[EmonFeedItem]] = []


class EmonFeedDataArgsModel(BaseModel):
    """
    Model for phpFina data endpoint arguments.

    Inherits:
        FileSourceModel: Provides the file source attribute.

    Attributes:
        feed_id (int):
            Feed ID (must be greater than 0).
    """
    host_slug: Annotated[
        str,
        Field(
            min_length=1,
            max_length=80,
            pattern=r"^[A-Za-z0-9_-]+$",
            title="Host Slug"
        )
    ]
    feed_id: Annotated[
        int,
        Field(
            gt=0,
            title="File ID"
        )
    ]


class GetFeedDataModel(EmonFeedDataArgsModel):
    """
    Model for retrieving phpFina data.

    Inherits:
        EmonFinaArgsModel: Provides the file source and feed ID.

    Attributes:
        start (int):
            Start time (must be greater than or equal to 0).
        interval (int):
            Interval time (must be greater than or equal to 0).
        window (int):
            Window time (must be greater than or equal to 0, default is 3600).
    """
    start: Annotated[
        int,
        Field(
            ge=0,
            default=0,
            title="Start time"
        )
    ]
    interval: Annotated[
        int,
        Field(
            ge=0,
            default=0,
            title="Interval time"
        )
    ]
    window: Annotated[
        int,
        Field(
            ge=0,
            default=3600,
            title="Window time"
        )
    ]


class FeedDataPoints(BaseModel):
    """
    File Meta Dict Type
    """
    success: bool
    id: int = 0
    name: str = ""
    data: list[list[Any]] = []
