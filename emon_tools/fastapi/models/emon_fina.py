"""
Emon Fina Pydantic models module.

This module defines the Pydantic models for the EmonFina API endpoints.
These models are used for request validation and documentation in FastAPI.
"""

from typing import Literal
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from emon_tools.fastapi.models.db import User


class EmonFinaBase(SQLModel):
    """
    Public item model for API responses.

    Inherits from EmonHostBase and adds id and owner_id fields.
    """
    id: int
    user: User
    file: User


class EmonFinaPublic(EmonFinaBase):
    """
    Public item model for API responses.

    Inherits from EmonHostBase and adds id and owner_id fields.
    """
    id: int


class EmonFinasPublic(SQLModel):
    """
    Container model for multiple public item representations.

    Attributes:
        data (list[EmonHostPublic]): List of public item models.
        count (int): Total count of items.
    """
    data: list[EmonFinaPublic]
    count: int


class FilePathModel(BaseModel):
    """
    Model for specifying the file path.

    Attributes:
        source (Literal["emoncms", "archive"]):
            Source path of phpFina files.
    """
    source: Annotated[
        Literal["emoncms", "archive"],
        Field(
            max_length=20,
            title="Source path of phpFina files"
        )
    ]


class FileSourceModel(BaseModel):
    """
    Model for specifying the file source.

    Attributes:
        source (Literal["emoncms", "archive"]):
            Source path of phpFina files.
    """
    source: Annotated[
        Literal["emoncms", "archive"],
        Field(
            max_length=20,
            title="Source path of phpFina files"
        )
    ]


class EmonFinaDataArgsModel(BaseModel):
    """
    Model for phpFina data endpoint arguments.

    Inherits:
        FileSourceModel: Provides the file source attribute.

    Attributes:
        feed_id (int):
            Feed ID (must be greater than 0).
    """
    file_id: Annotated[
        int,
        Field(
            gt=0,
            title="File ID"
        )
    ]


class EmonFinaArgsModel(FileSourceModel):
    """
    Model for phpFina data endpoint arguments.

    Inherits:
        FileSourceModel: Provides the file source attribute.

    Attributes:
        feed_id (int):
            Feed ID (must be greater than 0).
    """
    feed_id: Annotated[
        int,
        Field(
            gt=0,
            title="Feed ID"
        )
    ]


class GetFinaDataModel(EmonFinaDataArgsModel):
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
