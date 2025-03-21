"""Base Models"""
from typing import Any, Optional, Union
from pydantic import BaseModel


class ResponseError(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    table: Optional[str] = None
    field_name: Optional[str] = None
    error: Optional[str] = None


# Properties to return via API, id is always required
class ResponseModelBase(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool
    data: Any


class ResponseMessage(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool
    msg: str


class ResponseErrorBase(ResponseModelBase):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool = False
    msg: Optional[str]
    from_error: Optional[str]
    errors: Optional[list[Union[ResponseError, str]]]
    status_code: Optional[int]
