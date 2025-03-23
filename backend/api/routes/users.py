"""Users routes"""
import uuid
from typing import Any
from os.path import join as PathJoin
from pathlib import Path
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)
from pydantic import ValidationError
from sqlmodel import (
    col,
    delete,
    func,
    select
)
from backend.controllers.base import BaseController
from backend.core.config import settings
from backend.controllers.users import UserController
from backend.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from backend.core.security import get_password_hash
from backend.core.security import verify_password
from backend.models.db import (
    ArchiveFile,
    Category,
    EmonHost,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from backend.models.user import ResponseUploadedAvatar, ResponseUser
from backend.utils.files import FilesHelper
# pylint: disable=not-callable, broad-exception-caught

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
    responses=BaseController.get_error_responses()
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    try:
        count_statement = select(func.count()).select_from(User)
        count = session.exec(count_statement).one()

        statement = select(User).offset(skip).limit(limit)
        users = session.exec(statement).all()

        return UsersPublic(data=users, count=count)
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    responses=BaseController.get_error_responses()
)
def create_new_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    try:
        user = UserController.get_user_by_email(
            session=session, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The user with this email already exists "
                    "in the system."),
            )

        user = UserController.create_user(session=session, user_create=user_in)
        return user
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.post(
    "/upload_avatar/",
    response_model=ResponseUploadedAvatar,
    responses=BaseController.get_error_responses()
)
def update_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...)
) -> Any:
    """
    Update own user.
    """
    try:
        # Validate MIME type
        if file.content_type not in FilesHelper.ALLOWED_IMG_MIME_TYPES:
            raise ValidationError(
                "Invalid file mime type. Allowed types are: "
                f"{', '.join(FilesHelper.ALLOWED_IMG_MIME_TYPES)}"
            )
        # Validate file extension
        ext = FilesHelper.get_file_extension(file.filename)
        if ext not in FilesHelper.ALLOWED_IMG_EXTENSIONS:
            raise ValidationError(
                "Invalid file extension. Allowed extensions are: "
                f"{', '.join(FilesHelper.ALLOWED_IMG_EXTENSIONS)}"
            )
        # Optionally:
        # Check file size by reading first bytes (if file size is not known)
        # Note:
        # In production, we might configure a server-side limit
        # on the request size.
        contents = file.file.read(FilesHelper.MAX_IMG_FILE_SIZE + 1)
        if len(contents) > FilesHelper.MAX_IMG_FILE_SIZE:
            raise ValidationError(
                "File too large. Maximum allowed size is "
                f"{FilesHelper.MAX_IMG_FILE_SIZE} bytes"
            )
        # Reset file pointer after reading
        file.file.seek(0)
        # Generate a safe and unique filename
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = PathJoin(
            Path(settings.STATIC_BASE_PATH),
            unique_filename
        )

        with open(file_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                buffer.write(chunk)
        # Update the current user's avatar path (or URL)
        current_user.avatar = str(unique_filename)
        session.add(current_user)
        session.commit()
        return ResponseUploadedAvatar(
            success=True,
            msg=f"Successfully uploaded {file.filename}",
            avatar=unique_filename
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )
    finally:
        file.file.close()


@router.patch(
    "/update/me/",
    response_model=ResponseUser,
    responses=BaseController.get_error_responses()
)
def update_user_me(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe
) -> Any:
    """
    Update own user.
    """

    try:
        if user_in.email:
            existing_user = UserController.get_user_by_email(
                session=session,
                email=user_in.email
            )
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=409,
                    detail="User with this email already exists"
                )
        user_data = user_in.model_dump(exclude_unset=True)
        current_user.sqlmodel_update(user_data)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return ResponseUser(
            success=True,
            user=current_user
        )
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.patch(
    "/me/password/",
    response_model=Message,
    responses=BaseController.get_error_responses()
)
def update_password_me(
    *,
    session: SessionDep,
    body: UpdatePassword,
    current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    try:
        if not verify_password(
            body.current_password,
            current_user.hashed_password
        ):
            raise HTTPException(status_code=400, detail="Incorrect password")
        if body.current_password == body.new_password:
            raise HTTPException(
                status_code=400,
                detail="New password cannot be the same as the current one"
            )
        hashed_password = get_password_hash(body.new_password)
        current_user.hashed_password = hashed_password
        session.add(current_user)
        session.commit()
        return Message(message="Password updated successfully")
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/me/",
    response_model=UserPublic
)
def read_user_me(
    current_user: CurrentUser
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete(
    "/me/",
    response_model=Message,
    responses=BaseController.get_error_responses()
)
def delete_user_me(
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Delete own user.
    """
    try:
        if current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="Super users are not allowed to delete themselves"
            )
        session.delete(current_user)
        session.commit()
        return Message(message="User deleted successfully")
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.post(
    "/signup/",
    response_model=UserPublic,
    responses=BaseController.get_error_responses()
)
def register_user(
    session: SessionDep,
    user_in: UserRegister
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    try:
        user = UserController.get_user_by_email(
            session=session, email=user_in.email
        )
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system",
            )
        user_create = UserCreate.model_validate(user_in)
        user = UserController.create_user(
            session=session, user_create=user_create)
        return user
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.get(
    "/{user_id}/",
    response_model=UserPublic,
    responses=BaseController.get_error_responses()
)
def read_user_by_id(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    try:
        user = session.get(User, user_id)
        if user == current_user:
            return user
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="The user doesn't have enough privileges",
            )
        return user
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.patch(
    "/{user_id}/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    responses=BaseController.get_error_responses()
)
def update_current_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    try:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(
                status_code=404,
                detail="The user with this id does not exist in the system",
            )
        if user_in.email:
            existing_user = UserController.get_user_by_email(
                session=session,
                email=user_in.email
            )
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=409,
                    detail="User with this email already exists"
                )

        db_user = UserController.update_user(
            session=session,
            db_user=db_user,
            user_in=user_in
        )
        return db_user
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )


@router.delete(
    "/{user_id}/",
    dependencies=[Depends(get_current_active_superuser)],
    responses=BaseController.get_error_responses()
)
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user == current_user:
            raise HTTPException(
                status_code=403,
                detail="Super users are not allowed to delete themselves"
            )
        statement = delete(
            EmonHost).where(col(EmonHost.owner_id) == user_id)
        session.exec(statement)  # type: ignore
        statement = delete(Category).where(
            col(Category.owner_id) == user_id)
        session.exec(statement)  # type: ignore
        statement = delete(
            ArchiveFile).where(col(ArchiveFile.owner_id) == user_id)
        session.exec(statement)  # type: ignore
        session.delete(user)
        session.commit()
        return Message(message="User deleted successfully")
    except Exception as ex:
        BaseController.handle_exception(
            ex=ex,
            session=session
        )
