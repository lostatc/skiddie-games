"""Miscellaneous utilities.

Copyright © 2017 Wren Powell <wrenp@duck.com>

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
from typing import MutableMapping, Mapping


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
