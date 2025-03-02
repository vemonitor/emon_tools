"""
Module for security and authentication utilities.

This module provides functions for creating JWT access tokens,
verifying passwords, and generating password hashes. It uses the
PyJWT library for token generation and Passlib for password hashing.
"""
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

from fastapi import Cookie, HTTPException
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

from emon_tools.fastapi.core.config import settings
from emon_tools.fastapi.core.exceptions import InvalidToken


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta
) -> str:
    """
    Create a JWT access token.

    Parameters:
        subject (str | Any):
            The subject for the token, typically a user identifier.
        expires_delta (timedelta):
            The time duration after which the token expires.

    Returns:
        str:
            The encoded JWT access token as a string.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject)
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.TOKEN_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    expires_delta: timedelta
) -> str:
    """
    Create a JWT refresh token.

    Parameters:
        subject (str | Any):
            The subject for the token, typically a user identifier.
        expires_delta (timedelta):
            The time duration after which the token expires.

    Returns:
        str:
            The encoded JWT refresh token as a string.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.TOKEN_ALGORITHM
    )
    return encoded_jwt


def decode_refresh_token(token: str) -> uuid.UUID:
    """
    Decode a JWT refresh token and extract the user ID.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        if payload.get("type") != "refresh":
            raise InvalidToken("Not a refresh token")
        user_id = uuid.UUID(payload.get("sub"))
        return user_id
    except PyJWTError as ex:
        raise InvalidToken("Invalid refresh token") from ex


def get_refresh_token_from_cookie(refresh_token: str = Cookie(None)):
    """
    Get the refresh token from a cookie.
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    return refresh_token


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain text password against a hashed password.

    Parameters:
        plain_password (str):
            The plain text password to verify.
        hashed_password (str):
            The hashed password to compare against.

    Returns:
        bool:
            True if the plain password matches the hashed password,
            False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(
    password: str
) -> str:
    """
    Generate a hashed password from a plain text password.

    Parameters:
        password (str):
            The plain text password to hash.

    Returns:
        str:
            The generated hashed password.
    """
    return pwd_context.hash(password)
