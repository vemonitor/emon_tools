"""
Module for FastAPI authentication and dependency injection.

This module provides dependencies for obtaining a database session,
retrieving the current user from a JWT token, and ensuring the user has
active and superuser privileges.
"""
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from backend.core.config import settings
from backend.core.database import engine
from backend.models.db import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session.

    Yields:
        Session:
            A SQLAlchemy session connected to the database.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(
    session: SessionDep,
    token: TokenDep
) -> User:
    """
    Retrieve the current user from the JWT token.

    Parameters:
        session:
            A database session dependency.
        token:
            The JWT token extracted from request headers.

    Returns:
        User:
            The current authenticated user.

    Raises:
        HTTPException:
            If the JWT token is invalid, or the user is not found, or the
            user is inactive.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from ex
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(
    current_user: CurrentUser
) -> User:
    """
    Verify that the current user is an active superuser.

    Parameters:
        current_user:
            The currently authenticated user.

    Returns:
        User:
            The current active superuser.

    Raises:
        HTTPException:
            If the current user does not have superuser privileges.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
