"""
SQL Models module.

This module defines the SQLModel models for users and items,
including models for creation, update, and public representations.
It also includes models for authentication tokens and messages.
"""
from datetime import datetime
import enum
from typing import Optional
import uuid
import sqlalchemy as sa
from pydantic import EmailStr, model_validator
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel import func
from slugify import slugify
# pylint: disable=not-callable


# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ------- User
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Shared properties
class UserBase(SQLModel):
    """
    Base model for user properties.

    This model defines the common attributes shared by all user
    related models.
    """
    email: EmailStr = Field(
        sa_column=sa.Column(
            sa.String(255),
            unique=True,
            nullable=False,
            index=True
        )
    )
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    avatar: str | None = Field(default=None, max_length=255)


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
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        unique=True,
        max_length=36
    )
    hashed_password: str = Field(max_length=255)
    created_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now()
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            onupdate=func.now(),
            server_default=func.now()
        )
    )
    emonhost: list["EmonHost"] = Relationship(back_populates="owner")
    category: list["Category"] = Relationship(back_populates="owner")
    datapath: list["DataPath"] = Relationship(back_populates="owner")
    archivefile: list["ArchiveFile"] = Relationship(back_populates="owner")


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


# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ------- DataPath
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Shared properties
class DataPathType(str, enum.Enum):
    """
    DataPath type Enum
    """
    ARCHIVED = "archives"
    EMONCMS = "emoncms"


class DataFileType(str, enum.Enum):
    """
    DataPath type Enum
    """
    FINA = "fina"


class DataPathBase(SQLModel):
    """
    Base model for item properties.

    This model defines the common attributes for item-related models.
    """
    name: str = Field(unique=True, min_length=1, max_length=40)
    slug: str = Field(unique=True, min_length=1, max_length=40)
    path_type: DataPathType = Field(
        sa_column=sa.Column(
            sa.Enum(DataPathType)
        )
    )
    file_type: DataFileType = Field(
        sa_column=sa.Column(
            sa.Enum(DataFileType)
        )
    )
    path: str = Field(min_length=1, max_length=90)
    created_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now()
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            onupdate=func.now(),
            server_default=func.now()
        )
    )


class DataPathGenerators(DataPathBase):
    """
    EmonHostGenerators class inherits from EmonHostBase
    and provides functionality to generate a slug for the host.
    Methods:
        generate_slug(cls, values):
            Class method that generates a slug from the 'name' field
            in the provided values dictionary before model validation.
    """
    @model_validator(mode="before")
    @classmethod
    def generate_slug(cls, values):
        """Generate slug"""
        if 'name' in values:
            values["slug"] = slugify(values.get("name"))
        return values


class DataPathCreate(DataPathGenerators):
    """
    Model for DataPath registration via API.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
        full_name (str | None): The user's full name.
    """


# Properties to receive on item update
# type: ignore
class DataPathUpdate(DataPathGenerators):
    """
    Model for updating an Emon Host.

    Inherits from EmonHostBase, with fields made optional for updates.
    """


# Database model, database table inferred from class name
class DataPath(DataPathBase, table=True):
    """
    Database model representing an archive group.
    """
    id: Optional[int] = Field(
        default=None,
        sa_column=sa.Column(
            sa.Integer,
            primary_key=True,
            autoincrement=True,
            unique=True,
            index=True,
        ),
    )
    owner_id: str = Field(foreign_key="user.id", nullable=False, max_length=36)
    # Relationships
    owner: Optional["User"] = Relationship(
        back_populates="datapath"
    )
    emonhost: Optional["EmonHost"] = Relationship(
        back_populates="datapath"
    )
    archivefile: list["ArchiveFile"] = Relationship(
        back_populates="datapath"
    )


# Properties to return via API, id is always required
class DataPathPublic(DataPathBase):
    """
    Public item model for API responses.

    Inherits from DataPathBase and adds id and owner_id fields.
    """
    id: int
    owner_id: uuid.UUID
    path_type: str
    file_type: str


class DataPathsPublic(SQLModel):
    """
    Container model for multiple public item representations.

    Attributes:
        data (list[DataPathPublic]): List of public item models.
        count (int): Total count of items.
    """
    data: list[DataPathPublic]
    count: int


# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ------- EmonHost
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Shared properties
class EmonHostBase(SQLModel):
    """
    Base model for item properties.

    This model defines the common attributes for item-related models.
    """
    name: str = Field(min_length=1, max_length=40)
    slug: str = Field(unique=True, min_length=1, max_length=40)
    host: str | None = Field(default=None, max_length=255)
    api_key: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now()
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            onupdate=func.now(),
            server_default=func.now()
        )
    )


class EmonHostGenerators(EmonHostBase):
    """
    EmonHostGenerators class inherits from EmonHostBase
    and provides functionality to generate a slug for the host.
    Methods:
        generate_slug(cls, values):
            Class method that generates a slug from the 'name' field
            in the provided values dictionary before model validation.
    """
    @model_validator(mode="before")
    @classmethod
    def generate_slug(cls, values):
        """Generate slug"""
        if 'name' in values:
            values["slug"] = slugify(values.get("name"))
        return values


class EmonHostCreate(EmonHostGenerators):
    """
    Model for user registration via API.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
        full_name (str | None): The user's full name.
    """


# Properties to receive on item update
# type: ignore
class EmonHostUpdate(EmonHostGenerators):
    """
    Model for updating an Emon Host.

    Inherits from EmonHostBase, with fields made optional for updates.
    """


# Database model, database table inferred from class name
class EmonHost(EmonHostBase, table=True):
    """
    Database model representing an item.

    Inherits common properties from ItemBase and defines additional
    database-specific fields such as id, owner_id, and the owner
    relationship.
    """
    id: int | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.Integer,
            index=True,
            primary_key=True,
            unique=True,
            autoincrement=True
        )
    )
    owner_id: str = Field(foreign_key="user.id", nullable=False, max_length=36)
    datapath_id: int = Field(
        default=None,
        sa_column=sa.Column(
            sa.Integer,
            sa.ForeignKey("datapath.id")
        )
    )

    owner: User = Relationship(
        back_populates="emonhost")
    datapath: DataPath | None = Relationship(
        back_populates="emonhost")
    archivefile: list["ArchiveFile"] = Relationship(
        back_populates="emonhost")


# Properties to return via API, id is always required
class EmonHostPublic(EmonHostBase):
    """
    Public item model for API responses.

    Inherits from EmonHostBase and adds id and owner_id fields.
    """
    id: int
    owner_id: uuid.UUID
    datapath: DataPath | None


class EmonHostsPublic(SQLModel):
    """
    Container model for multiple public item representations.

    Attributes:
        data (list[EmonHostPublic]): List of public item models.
        count (int): Total count of items.
    """
    data: list[EmonHostPublic]
    count: int


# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ------- Category
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Shared properties
class CategoryType(str, enum.Enum):
    """
    Category type Enum
    """
    FINA_FILES = "fina_files"
    FINA_PATHS = "fina_paths"


class CategoryBase(SQLModel):
    """
    Base model for item properties.

    This model defines the common attributes for item-related models.
    """
    name: str = Field(unique=True, min_length=1, max_length=40)
    slug: str = Field(unique=True, min_length=1, max_length=40)
    type: CategoryType = Field(
        sa_column=sa.Column(
            sa.Enum(CategoryType)
        )
    )
    created_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now()
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            onupdate=func.now(),
            server_default=func.now()
        )
    )


class CategoryGenerators(CategoryBase):
    """
    EmonHostGenerators class inherits from EmonHostBase
    and provides functionality to generate a slug for the host.
    Methods:
        generate_slug(cls, values):
            Class method that generates a slug from the 'name' field
            in the provided values dictionary before model validation.
    """
    @model_validator(mode="before")
    @classmethod
    def generate_slug(cls, values):
        """Generate slug"""
        if 'name' in values:
            values["slug"] = slugify(values.get("name"))
        return values


class CategoryCreate(CategoryGenerators):
    """
    Model for Category registration via API.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
        full_name (str | None): The user's full name.
    """


# Properties to receive on item update
# type: ignore
class CategoryUpdate(CategoryGenerators):
    """
    Model for updating an Emon Host.

    Inherits from EmonHostBase, with fields made optional for updates.
    """


# Database model, database table inferred from class name
class Category(CategoryBase, table=True):
    """
    Database model representing an archive group.
    """
    id: Optional[int] = Field(
        default=None,
        sa_column=sa.Column(
            sa.Integer,
            primary_key=True,
            autoincrement=True,
            unique=True,
            index=True,
        ),
    )
    owner_id: str = Field(foreign_key="user.id", nullable=False, max_length=36)
    # Relationships
    owner: Optional["User"] = Relationship(
        back_populates="category"
    )
    archivefile: list["ArchiveFile"] = Relationship(
        back_populates="category"
    )


# Properties to return via API, id is always required
class CategoryPublic(CategoryBase):
    """
    Public item model for API responses.

    Inherits from CategoryBase and adds id and owner_id fields.
    """
    id: int
    owner_id: uuid.UUID


class CategorysPublic(SQLModel):
    """
    Container model for multiple public item representations.

    Attributes:
        data (list[CategoryPublic]): List of public item models.
        count (int): Total count of items.
    """
    data: list[CategoryPublic]
    count: int


# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ------- ArchiveFile
# ---------------------------------------------------------------
# ---------------------------------------------------------------
class ArchiveFileBase(SQLModel):
    """
    Base model for item properties.

    This model defines the common attributes for item-related models.
    """
    name: str = Field(min_length=1, max_length=40)
    slug: str = Field(unique=True, min_length=1, max_length=40)
    file_name: str = Field(min_length=1, max_length=50)
    start_time: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True)
        )
    )
    end_time: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True)
        )
    )
    interval: int = Field(ge=0, default=0)
    size: int = Field(ge=0, default=0)
    npoints: int = Field(ge=0, default=0)
    feed_id: int = Field(
        default=0,
        sa_column=sa.Column(sa.Integer, nullable=True)
    )
    sha_256: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )
    created_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            server_default=func.now()
        )
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            onupdate=func.now(),
            server_default=func.now()
        )
    )


class ArchiveFileGenerators(ArchiveFileBase):
    """
    EmonHostGenerators class inherits from EmonHostBase
    and provides functionality to generate a slug for the host.
    Methods:
        generate_slug(cls, values):
            Class method that generates a slug from the 'name' field
            in the provided values dictionary before model validation.
    """
    category_id: int | None = Field(
        default=None,
        gt=0,
        sa_column=sa.Column(
            sa.Integer,
            index=True,
        )
    )
    datapath_id: int | None = Field(
        default=None,
        gt=0,
        sa_column=sa.Column(
            sa.Integer,
            index=True,
        )
    )
    emonhost_id: int | None = Field(
        default=None,
        gt=0,
        sa_column=sa.Column(
            sa.Integer,
            index=True,
        )
    )

    @model_validator(mode="before")
    @classmethod
    def generate_slug(cls, values):
        """Generate slug"""
        if 'name' in values:
            values["slug"] = slugify(values.get("name"))
        return values


class ArchiveFileCreate(ArchiveFileGenerators):
    """
    Model for ArchiveFile registration via API.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
        full_name (str | None): The user's full name.
    """


# Properties to receive on item update
# type: ignore
class ArchiveFileUpdate(ArchiveFileGenerators):
    """
    Model for updating an Emon Host.

    Inherits from EmonHostBase, with fields made optional for updates.
    """


# Database model, database table inferred from class name
class ArchiveFile(ArchiveFileBase, table=True):
    """
    Database model representing an item.

    Inherits common properties from ItemBase and defines additional
    database-specific fields such as id, owner_id, and the owner
    relationship.
    """
    id: int | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.Integer,
            index=True,
            primary_key=True,
            unique=True,
            autoincrement=True
        )
    )
    owner_id: str = Field(foreign_key="user.id", nullable=False, max_length=36)
    category_id: int | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.Integer,
            sa.ForeignKey("category.id")
        )
    )
    datapath_id: int = Field(
        sa_column=sa.Column(
            sa.Integer,
            sa.ForeignKey("datapath.id")
        )
    )
    emonhost_id: int | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.Integer,
            sa.ForeignKey("emonhost.id")
        )
    )
    owner: User | None = Relationship(back_populates="archivefile")
    category: Category | None = Relationship(
        back_populates="archivefile")
    datapath: DataPath | None = Relationship(
        back_populates="archivefile")
    emonhost: EmonHost | None = Relationship(
        back_populates="archivefile")


# Properties to return via API, id is always required
class ArchiveFilePublic(ArchiveFileBase):
    """
    Public item model for API responses.

    Inherits from ArchiveFileBase and adds id and owner_id fields.
    """
    id: int
    category: Category | None
    datapath: DataPath | None
    emonhost: EmonHost | None
    owner_id: uuid.UUID


class ArchiveFilesPublic(SQLModel):
    """
    Container model for multiple public item representations.

    Attributes:
        data (list[ArchiveFilePublic]): List of public item models.
        count (int): Total count of items.
    """
    data: list[ArchiveFilePublic]
    count: int


# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ------- Message
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Generic message
class Message(SQLModel):
    """
    Generic message model for API responses.

    Attributes:
        message (str): A message string.
    """
    message: str


# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ------- Token
# ---------------------------------------------------------------
# ---------------------------------------------------------------
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
