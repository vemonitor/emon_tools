"""Base Models"""
from typing import Optional
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


class ResponseSuccessBase(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    data: Optional[dict]


class ResponseSimpleErrorBase(ResponseModelBase):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    errors: Optional[list[ResponseError]]


class ResponseErrorBase(ResponseSimpleErrorBase):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    msg: Optional[str]
    from_error: Optional[str]
    errors: Optional[list[ResponseError]]
    status_code: Optional[int]
