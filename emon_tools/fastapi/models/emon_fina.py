"""emon_fina pydantic models."""
from typing import Literal
from typing_extensions import Annotated
from pydantic import BaseModel, Field


class FileSourceModel(BaseModel):
    """Get PhpFina data endpoint args"""
    source: Annotated[Literal["emoncms", "archive"], Field(
        max_length=20,
        title="Source path of phpFina files")]


class EmonFinaArgsModel(FileSourceModel):
    """Get PhpFina data endpoint args"""
    feed_id: Annotated[int, Field(gt=0, title="Feed ID")]


class GetFinaDataModel(EmonFinaArgsModel):
    """Get PhpFina data endpoint args"""
    start: Annotated[int, Field(
        ge=0, default=0, title="Start time")]
    interval: Annotated[int, Field(
        ge=0, default=0, title="Interval time")]
    window: Annotated[int, Field(
        ge=0, default=3600, title="Window time")]
