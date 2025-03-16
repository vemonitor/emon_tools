"""
Base controller
"""
from typing import Union
from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from emon_tools.fastapi.models.base import (
    ResponseErrorBase,
    ResponseSimpleErrorBase
)
from emon_tools.fastapi.utils.errors_parser import (
    parse_integrity_error,
    parse_pydantic_errors
)


class BaseController:
    """
    Base controller
    """
    @staticmethod
    def handle_exception(
        ex: Exception,
        session: Union[Session, None] = None
    ):
        """
        Handles exceptions in a unified manner.

        Args:
            ex (Exception): The exception that occurred.
            session (Session, optional):
            The database session, required for rollback in case of DB errors.

        Returns:
            ResponseModelBase: A properly formatted API response.
        """
        if isinstance(ex, IntegrityError):
            if session:
                session.rollback()
            return ResponseErrorBase(
                success=False,
                msg=(
                    "Database integrity error: "
                    "Possibly duplicate entry or invalid reference."
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
                from_error="IntegrityError",
                errors=parse_integrity_error(ex),
            )

        elif isinstance(ex, ValidationError):
            if session:
                session.rollback()
            return ResponseErrorBase(
                success=False,
                msg="Validation error.",
                from_error="ValidationError",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=parse_pydantic_errors(ex),
            )

        elif isinstance(ex, (ValueError, TypeError, IOError)):
            return ResponseSimpleErrorBase(
                success=False,
                errors=[str(ex)]
            )

        if session:
            session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(ex)}"
        ) from ex
