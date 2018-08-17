"""Classes for generating random data for the table.

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
import abc
import random
from typing import List, Optional, Sequence


class ColumnData:
    """The data that exists in a column.

    Attributes:
        name: The name of the column.
        rows: The data contained in the column as a list of rows.
    """
    def __init__(self, name: str, rows: List[str]):
        self.name = name
        self.rows = rows

    @property
    def num_rows(self) -> int:
        """The number of rows in the column."""
        return len(self.rows)


class ColumnGenerator(abc.ABC):
    """A data type that can appear in the table window in the game.

    Attributes:
        names: All the possible column names for this data type.
    """
    def __init__(self, names: List[str]) -> None:
        self.names = names

    def _generate_from_data(self, data: List[str]) -> ColumnData:
        """Return a ColumnData instance with the given data and a random name."""
        name = random.choice(self.names)
        return ColumnData(name, data)

    @abc.abstractmethod
    def generate(self, rows: int) -> ColumnData:
        """Generate random column data.

        Args:
            rows: The number of rows of data to generate.
        """


class ContinuousColumnGenerator(ColumnGenerator):
    """A continuous data type that can appear in the table window in the game."""
    def __init__(self, names: List[str]) -> None:
        super().__init__(names)

    @staticmethod
    def _select_from_range(min_value: int, max_value: int, items: int) -> Sequence[int]:
        """Randomly select a given number of integers from the given range.

        Args:
            min_value: The minimum value to select.
            max_value: The maximum value to select.
            items: The number of values to select.

        Returns:
            A sorted sequence of integers without repeats.
        """
        remaining_ints = list(range(min_value, max_value+1))
        result = []
        for _ in range(items):
            next_int = random.choice(remaining_ints)
            result.append(next_int)
            remaining_ints.remove(next_int)

        result.sort()
        return result

    @abc.abstractmethod
    def generate(self, rows: int) -> ColumnData:
        pass


class AgeColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a person's age."""
    min_value = 0
    max_value = 90

    def __init__(self) -> None:
        names = ["age"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        values = self._select_from_range(self.min_value, self.max_value, rows)
        data = [str(value) for value in values]
        return self._generate_from_data(data)


class DiscreteColumnGenerator(ColumnGenerator):
    """A discrete data type that can appear in the table window in the game.

    Args:
        possible_values: The list of possible values that can appear in the column.
        max_discrete_values: The maximum number of unique discrete values. If None, then there's no maximum.

    Attributes:
        possible_values: The list of possible values that can appear in the column.
        max_discrete_values: The number of different values that appear in the returned data will not exceed this
            number.
    """
    def __init__(self, names: List[str], possible_values: List[str], max_discrete_values: Optional[int] = None) -> None:
        self.possible_values = possible_values
        self.max_discrete_values = max_discrete_values or len(self.possible_values)

        if self.max_discrete_values <= 1:
            raise ValueError("There must be more than one possible value")

        super().__init__(names)

    def _limit_values(self, values: List[str]) -> List[str]:
        """Return a random subset of the given values that does not exceed `self.max_discrete_values`."""
        try:
            return random.sample(set(values), self.max_discrete_values)
        except ValueError:
            return values

    def generate(self, rows: int) -> ColumnData:
        possible_values = self._limit_values(self.possible_values)
        data = [random.choice(possible_values) for _ in range(rows)]
        return self._generate_from_data(data)


class BooleanColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing boolean values."""
    def __init__(self, max_discrete_values: Optional[int] = None) -> None:
        names = ["exists", "preferred", "enabled", "open", "active"]
        possible_values = ["true", "false"]
        super().__init__(names, possible_values, max_discrete_values)
