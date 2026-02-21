from datetime import datetime
from decimal import Decimal
from typing import Any, List, Dict, TypeVar, Union
import uuid

T = TypeVar('T')

class ValidatingBaseModel:
    """Base class providing common validation helper methods for domain models."""

    def _validate_not_none(self, value: T, field_name: str) -> T:
        """Ensures a value is not None."""
        if value is None:
            raise ValueError(f"{field_name} cannot be None.")
        return value

    def _validate_type(self, value: Any, expected_type: type, field_name: str, allow_none: bool = False) -> Any:
        """Ensures a value is of a specific type, optionally allowing None."""
        if allow_none and value is None:
            return value
        if not isinstance(value, expected_type):
            raise TypeError(f"{field_name} must be of type {expected_type.__name__}, got {type(value).__name__}.")
        return value

    def _validate_string_not_empty(self, value: str, field_name: str, max_length: int = None, allow_none: bool = False) -> Union[str, None]:
        """Ensures a string is not empty, optionally allowing None and checking max length."""
        value = self._validate_type(value, str, field_name, allow_none)
        if value is None:
            return None
        if not value.strip():
            raise ValueError(f"{field_name} cannot be an empty string.")
        if max_length is not None and len(value) > max_length:
            raise ValueError(f"{field_name} exceeds maximum length of {max_length}.")
        return value

    def _validate_decimal_non_negative(self, value: Decimal, field_name: str, allow_none: bool = False) -> Union[Decimal, None]:
        """Ensures a Decimal is non-negative, optionally allowing None."""
        value = self._validate_type(value, Decimal, field_name, allow_none)
        if value is None:
            return None
        if value < 0:
            raise ValueError(f"{field_name} cannot be negative.")
        return value

    def _validate_list_of_strings(self, value: List[str], field_name: str, allow_none: bool = False) -> Union[List[str], None]:
        """Ensures a value is a list of strings, optionally allowing None."""
        value = self._validate_type(value, list, field_name, allow_none)
        if value is None:
            return None
        if not all(isinstance(item, str) for item in value):
            raise TypeError(f"{field_name} must be a list of strings.")
        return value

    def _validate_dict(self, value: Dict, field_name: str, allow_none: bool = False) -> Union[Dict, None]:
        """Ensures a value is a dict, optionally allowing None."""
        return self._validate_type(value, dict, field_name, allow_none)

    def _validate_datetime(self, value: datetime, field_name: str, allow_none: bool = False) -> Union[datetime, None]:
        """Ensures a value is a datetime object, optionally allowing None."""
        return self._validate_type(value, datetime, field_name, allow_none)

    def _validate_boolean(self, value: bool, field_name: str, allow_none: bool = False) -> Union[bool, None]:
        """Ensures a value is a boolean, optionally allowing None."""
        return self._validate_type(value, bool, field_name, allow_none)

    def _validate_float(self, value: float, field_name: str, allow_none: bool = False) -> Union[float, None]:
        """Ensures a value is a float, optionally allowing None."""
        return self._validate_type(value, float, field_name, allow_none)

    def _validate_uuid(self, value: uuid.UUID, field_name: str, allow_none: bool = False) -> Union[uuid.UUID, None]:
        """Ensures a value is a UUID object, optionally allowing None."""
        return self._validate_type(value, uuid.UUID, field_name, allow_none)
