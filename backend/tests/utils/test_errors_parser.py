import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from backend.utils.errors_parser import parse_integrity_error, parse_pydantic_errors


class TestErrorParsers:

    def test_parse_integrity_error_unique_constraint(self):
        exc = IntegrityError("Duplicate entry '123' for key 'users.email'", None, None)
        exc.orig = "Duplicate entry '123' for key 'users.email'"
        expected = [{
            "table": "users",
            "field_name": "email",
            "error": "Duplicate entry: '123' already exists."
        }]
        result = parse_integrity_error(exc)
        assert result == expected

    def test_parse_integrity_error_foreign_key_constraint(self):
        exc = IntegrityError("FOREIGN KEY (`user_id`) REFERENCES `users`", None, None)
        exc.orig = "FOREIGN KEY (`user_id`) REFERENCES `users`"
        expected = [{
            "table": "users",
            "field_name": "user_id",
            "error": "Invalid foreign key reference in 'user_id'."
        }]
        result = parse_integrity_error(exc)
        assert result == expected

    def test_parse_integrity_error_not_null_constraint(self):
        exc = IntegrityError("Column 'email' cannot be null", None, None)
        exc.orig = "Column 'email' cannot be null"
        expected = [{
            "table": None,
            "field_name": "email",
            "error": "Field 'email' cannot be null."
        }]
        result = parse_integrity_error(exc)
        assert result == expected

    def test_parse_integrity_error_default_constraint(self):
        exc = IntegrityError("Field 'created_at' doesn't have a default value", None, None)
        exc.orig = "Field 'created_at' doesn't have a default value"
        expected = [{
            "table": None,
            "field_name": "created_at",
            "error": "Field 'created_at' requires a value."
        }]
        result = parse_integrity_error(exc)
        assert result == expected

    def test_parse_integrity_error_unknown(self):
        exc = IntegrityError("Some unknown error", None, None)
        exc.orig = "Some unknown error"
        expected = [{
            "table": None,
            "field_name": None,
            "error": "Unknown database integrity error"
        }]
        result = parse_integrity_error(exc)
        assert result == expected

    def test_parse_integrity_error_multiple_errors(self):
        exc = IntegrityError(
            "Duplicate entry '123' for key 'users.email'; "
            "FOREIGN KEY (`user_id`) REFERENCES `users`; "
            "Column 'email' cannot be null; "
            "Field 'created_at' doesn't have a default value",
            None, None
        )
        exc.orig = (
            "Duplicate entry '123' for key 'users.email'; "
            "FOREIGN KEY (`user_id`) REFERENCES `users`; "
            "Column 'email' cannot be null; "
            "Field 'created_at' doesn't have a default value"
        )
        expected = [
            {
                "table": "users",
                "field_name": "email",
                "error": "Duplicate entry: '123' already exists."
            },
            {
                "table": "users",
                "field_name": "user_id",
                "error": "Invalid foreign key reference in 'user_id'."
            },
            {
                "table": None,
                "field_name": "email",
                "error": "Field 'email' cannot be null."
            },
            {
                "table": None,
                "field_name": "created_at",
                "error": "Field 'created_at' requires a value."
            }
        ]
        result = parse_integrity_error(exc)
        assert result == expected

    def test_parse_pydantic_errors(self):
        errors = [
            {
                "loc": ["body", "name"],
                "msg": "field required",
                "type": "value_error.missing"
            },
            {
                "loc": ["body", "age"],
                "msg": "value is not a valid integer",
                "type": "type_error.integer"
            }
        ]
        exc = ValidationError(errors)
        expected = [
            {"field_name": "body.name", "error": "field required"},
            {"field_name": "body.age", "error": "value is not a valid integer"}
        ]
        result = parse_pydantic_errors(exc)
        assert result == expected

    def test_parse_pydantic_errors_empty(self):
        """
        Test parsing pydantic errors when there are no errors.
        """
        errors = []
        exc = ValidationError(errors)
        expected = []
        result = parse_pydantic_errors(exc)
        assert result == expected

    def test_parse_pydantic_errors_multiple(self):
        errors = [
            {
                "loc": ["body", "name"],
                "msg": "field required",
                "type": "value_error.missing"
            },
            {
                "loc": ["body", "age"],
                "msg": "value is not a valid integer",
                "type": "type_error.integer"
            },
            {
                "loc": ["body", "email"],
                "msg": "invalid email format",
                "type": "value_error.email"
            }
        ]
        exc = ValidationError(errors, model=None)
        expected = [
            {"field_name": "body.name", "error": "field required"},
            {"field_name": "body.age", "error": "value is not a valid integer"},
            {"field_name": "body.email", "error": "invalid email format"}
        ]
        result = parse_pydantic_errors(exc)
        assert result == expected
