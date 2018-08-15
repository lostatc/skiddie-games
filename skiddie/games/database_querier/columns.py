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
from typing import List


class ColumnData:
    """The data that exists in a column.

    Attributes:
        name: The name of the column.
        data: The data contained in the column as a list of rows.
    """
    def __init__(self, name: str, data: List[str]):
        self.name = name
        self.data = data

    @property
    def rows(self) -> int:
        """The number of rows in the column."""
        return len(self.data)


class TableColumn(abc.ABC):
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


class ContinuousTableColumn(TableColumn):
    """A continuous data type that can appear in the table window in the game."""
    def __init__(self, names: List[str]) -> None:
        super().__init__(names)

    @abc.abstractmethod
    def generate(self, rows: int) -> ColumnData:
        pass


class AgeColumn(ContinuousTableColumn):
    """A continuous data type representing a person's age."""
    min_value = 0
    max_value = 90

    def __init__(self) -> None:
        names = ["age"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        data = [random.randint(self.min_value, self.max_value) for _ in range(rows)]
        data.sort()
        return self._generate_from_data(data)


class DiscreteTableColumn(TableColumn):
    """A discrete data type that can appear in the table window in the game.

    Attributes:
        max_different_values: The number of different values that appear in the returned data will not exceed this
            number.
    """
    def __init__(self, names: List[str], max_different_values: int) -> None:
        self.max_different_values = max_different_values
        super().__init__(names)

    def _limit_values(self, values: List[str]) -> List[str]:
        """Return a random subset of the given values that does not exceed `max_different_values`."""
        try:
            return random.sample(set(values), self.max_different_values)
        except ValueError:
            return values

    @abc.abstractmethod
    def generate(self, rows: int) -> ColumnData:
        pass


class BooleanColumn(DiscreteTableColumn):
    """A discrete data type representing boolean values."""
    possible_values = ["true", "false"]

    def __init__(self, max_different_values: int) -> None:
        names = ["exists", "preferred", "enabled", "open", "active"]
        super().__init__(names, max_different_values)

    def generate(self, rows: int) -> ColumnData:
        possible_values = self._limit_values(self.possible_values)
        data = [random.choice(possible_values) for _ in range(rows)]
        return self._generate_from_data(data)
