"""
Provides non-application element specific utility functions
"""
from __future__ import annotations

import typing


def is_true(value: typing.Any) -> bool:
    """
    Determines if the passed value indicates truth.

    Example:
        >>> is_true('true')
        True
        >>> is_true('T')
        True
        >>> is_true('False')
        False
        >>> is_true('Dorothy')
        False
        >>> is_true(0)
        False

    :param value: The value to test
    :return: True if the value should be considered truthy
    """
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, str):
        return value.lower() in ("true", "t", 'yes', 'y', 'o', 'on', '1')

    return bool(value)
