"""
Module for security and authentication utilities.

This module provides functions for creating JWT access tokens,
verifying passwords, and generating password hashes. It uses the
PyJWT library for token generation and Passlib for password hashing.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from emon_tools.fastapi.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

ALGORITHM = "HS256"


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
        algorithm=ALGORITHM
    )
    return encoded_jwt


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
