"""Miscellaneous utilities.

Copyright © 2017-2018 Wren Powell <wrenp@duck.com>

This file is part of skiddie.

skiddie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

skiddie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with skiddie.  If not, see <http://www.gnu.org/licenses/>.
"""
import time
import functools
from typing import MutableMapping, Mapping, Callable, Any, TypeVar

T = TypeVar("T")


def recursive_update(update: MutableMapping, other: Mapping) -> MutableMapping:
    """Recursively update `update` with values from `other`, overwriting existing keys."""
    for key, value in other.items():
        if isinstance(value, Mapping):
            update[key] = recursive_update(update.get(key, {}), value)
        else:
            update[key] = value
    return update


class LateInit:
    """Raise an exception if the attribute is unset.

    Args:
        message: The message passed to the exception when the value is accessed before it is set.
    """
    def __init__(self, message: str = "this value must not be None") -> None:
        self._value = None
        self._message = message

    def __get__(self, instance, owner):
        if self._value is None:
            raise ValueError(self._message)
        return self._value

    def __set__(self, instance, value):
        self._value = value


def get_timer(func: Callable) -> Callable[..., float]:
    """Get a function which times how long it takes to complete the given function.

    Args:
        func: The function to time the execution of.

    Returns:
        A function which returns the number of seconds that the given function took to execute.
    """
    def timer(*args, **kwargs) -> float:
        start_time = time.monotonic()
        func(*args, **kwargs)
        end_time = time.monotonic()

        elapsed_time = end_time - start_time

        return elapsed_time

    return timer


def get_first_insensitive_key(mapping: Mapping[str, T], match_key: str) -> T:
    """"""
    """Get the name of the first key which is a case-insensitive match.

    Args:
        mapping: The mapping to get the key from.
        match_key: The key to search for.

    Raises:
        ValueError: The given key does not appear in the mapping.
    """
    try:
        return next(key for key, value in mapping.items() if key.lower() == match_key.lower())
    except StopIteration:
        raise ValueError("The given key does not appear in the mapping")


def get_first_insensitive_value(mapping: Mapping[str, T], match_key: str) -> T:
    """Get the value of the first key which is a case-insensitive match.

    Args:
        mapping: The mapping to get the value from.
        match_key: The key to get the value of.

    Raises:
        ValueError: The given key does not appear in the mapping.
    """
    try:
        return next(value for key, value in mapping.items() if key.lower() == match_key.lower())
    except StopIteration:
        raise ValueError("The given key does not appear in the mapping")
