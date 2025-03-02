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
    msg: Optional[str] = None
    from_error: Optional[str] = None
    errors: Optional[list[ResponseError]] = None
    status_code: Optional[int] = None
    data: Optional[dict] = None
