"""
User models
"""


from pydantic import BaseModel

from backend.models.db import UserPublic


class ResponseUploadedAvatar(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool
    msg: str
    avatar: str


class ResponseUser(BaseModel):
    """
    Public item model for API responses.

    Inherits from ResponseModelBase and adds id and owner_id fields.
    """
    success: bool
    user: UserPublic
