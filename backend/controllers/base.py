"""
Base controller
"""
from typing import Union
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from backend.models.base import (
    ResponseErrorBase
)
from backend.utils.errors_parser import (
    parse_integrity_error,
    parse_pydantic_errors
)


class BaseController:
    """
    Base controller
    """
    @staticmethod
    def get_error_responses():
        """Get error responses request model"""
        return {
            500: {
                "model": ResponseErrorBase
            }
        }

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
        content = None
        if isinstance(ex, IntegrityError):
            content = ResponseErrorBase(
                success=False,
                msg=(
                    "Database integrity error: "
                    "Possibly duplicate entry or invalid reference."
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
                from_error="IntegrityError",
                errors=parse_integrity_error(ex),
            )

        if isinstance(ex, ValidationError):
            content = ResponseErrorBase(
                success=False,
                msg="Validation error.",
                from_error="ValidationError",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=parse_pydantic_errors(ex),
            )

        if isinstance(ex, (ValueError, TypeError, IOError)):
            content = ResponseErrorBase(
                success=False,
                msg="Internal Error.",
                from_error="EmonToolsError",
                errors=[str(ex)],
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if session:
            session.rollback()

        if content is None:
            content = ResponseErrorBase(
                success=False,
                msg="An unexpected error occurred",
                from_error="Exeption",
                errors=[str(ex)],
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content.model_dump()
        )
