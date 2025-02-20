"""
SQL Models module.

This module defines the SQLModel models for users and items,
including models for creation, update, and public representations.
It also includes models for authentication tokens and messages.
"""

import uuid
import sqlalchemy as sa
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    """
    Base model for user properties.

    This model defines the common attributes shared by all user
    related models.
    """
    email: EmailStr = Field(
        sa_column=sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    )
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """
    Model for creating a new user.

    Inherits the common user properties from UserBase and adds
    a password field required for user creation.
    """
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """
    Model for user registration via API.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
        full_name (str | None): The user's full name.
    """
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
# type: ignore
class UserUpdate(UserBase):
    """
    Model for updating user details via API.

    Inherits from UserBase, with all fields optional for update.
    """
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """
    Model for users updating their own profile.

    Attributes:
        full_name (str | None): The user's full name.
        email (EmailStr | None): The user's email address.
    """
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """
    Model for updating a user's password.

    Attributes:
        current_password (str): The current password.
        new_password (str): The new password.
    """
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    """
    Database model representing a user.

    Inherits common properties from UserBase and defines additional
    database-specific fields such as id, hashed_password, and the
    relationship to items.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True, max_length=36)
    hashed_password: str = Field(max_length=255)

    items: list["Item"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    """
    Public user model for API responses.

    Inherits from UserBase and adds the user id, which is always
    required for public representations.
    """
    id: uuid.UUID


class UsersPublic(SQLModel):
    """
    Container model for multiple public user representations.

    Attributes:
        data (list[UserPublic]): List of public user models.
        count (int): Total count of users.
    """
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    """
    Base model for item properties.

    This model defines the common attributes for item-related models.
    """
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    """
    Model for creating a new item.

    Inherits all properties from ItemBase.
    """


# Properties to receive on item update
# type: ignore
class ItemUpdate(ItemBase):
    """
    Model for updating an item.

    Inherits from ItemBase, with fields made optional for updates.
    """
    title: str | None = Field(default=None, min_length=1, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    """
    Database model representing an item.

    Inherits common properties from ItemBase and defines additional
    database-specific fields such as id, owner_id, and the owner
    relationship.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, unique=True, max_length=36)
    owner_id: str = Field(foreign_key="user.id", nullable=False, max_length=36)

    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    """
    Public item model for API responses.

    Inherits from ItemBase and adds id and owner_id fields.
    """
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    """
    Container model for multiple public item representations.

    Attributes:
        data (list[ItemPublic]): List of public item models.
        count (int): Total count of items.
    """
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    """
    Generic message model for API responses.

    Attributes:
        message (str): A message string.
    """
    message: str


# JSON payload containing access token
class Token(SQLModel):
    """
    Model representing a JWT access token response.

    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The token type (default is "bearer").
    """
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    """
    Model representing the contents of a JWT token payload.

    Attributes:
        sub (str | None): The subject (typically the user id) of the token.
    """
    sub: str | None = None


class NewPassword(SQLModel):
    """
    Model for resetting a user's password.

    Attributes:
        token (str): The password reset token.
        new_password (str): The new password.
    """
    token: str
    new_password: str = Field(
        min_length=8, max_length=40
    )
