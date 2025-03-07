"""Api error parsers"""
import re
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


def parse_integrity_error(exc: IntegrityError) -> list[dict]:
    """
    Parses IntegrityError and returns a list of error details.

    Returns:
    [
        {"table": <table_name>, "field_name": <column>, "error": <message>},
        ...
    ]
    """
    error_message = str(exc.orig)  # Raw DB error message
    errors = []

    # ✅ UNIQUE constraint violation (multiple possible)
    unique_matches = re.findall(
        r"Duplicate entry '(.+)' for key '([^'.]+)\.([^'.]+)'", error_message
    )
    for match in unique_matches:
        errors.append({
            "table": match[1],  # Table name
            "field_name": match[2],  # Field name
            "error": f"Duplicate entry: '{match[0]}' already exists."
        })

    # ✅ FOREIGN KEY constraint violation (multiple possible)
    fk_matches = re.findall(
        r"FOREIGN KEY \(`(.+?)`\) REFERENCES `(.+?)`",
        error_message
    )
    for match in fk_matches:
        errors.append({
            "table": match[1],  # Referenced table
            "field_name": match[0],  # Field name
            "error": f"Invalid foreign key reference in '{match[0]}'."
        })

    # ✅ NOT NULL constraint violation (multiple possible)
    not_null_matches = re.findall(
        r"Column '(.+?)' cannot be null", error_message
    )
    for match in not_null_matches:
        errors.append({
            "table": None,  # Table not always available in error message
            "field_name": match,  # Field name
            "error": f"Field '{match}' cannot be null."
        })

    # ✅ DEFAULT constraint violation (multiple possible)
    default_matches = re.findall(
        r"Field '(.+?)' doesn't have a default value", error_message
    )
    for match in default_matches:
        errors.append({
            "table": None,  # Table not always available in error message
            "field_name": match,  # Field name
            "error": f"Field '{match}' requires a value."
        })

    # If no matches, return a generic message
    if not errors:
        errors.append({
            "table": None,
            "field_name": None,
            "error": "Unknown database integrity error"
        })

    return errors


def parse_pydantic_errors(exc: ValidationError) -> list[dict]:
    """
    Parses Pydantic validation errors into a structured list.

    Returns:
    [
        {"field_name": <field_name>, "error": <original_error_message>},
        ...
    ]
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation error")
        errors.append({"field_name": field, "error": message})

    return errors
