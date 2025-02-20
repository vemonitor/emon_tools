"""
Emon Fina Pydantic models module.

This module defines the Pydantic models for the EmonFina API endpoints.
These models are used for request validation and documentation in FastAPI.
"""

from typing import Literal
from typing_extensions import Annotated
from pydantic import BaseModel, Field


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


class GetFinaDataModel(EmonFinaArgsModel):
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