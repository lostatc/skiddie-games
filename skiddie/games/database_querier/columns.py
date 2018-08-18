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
import datetime
import random
from typing import List, Optional, Sequence, TypeVar

from skiddie.utils import take_random_cycle

T = TypeVar("T")


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
    def _sample_and_sort(sequence: Sequence[T], num_items: int) -> Sequence[T]:
        """Randomly sample a given number of integers from the given sequence and sort them."""
        return sorted(random.sample(sequence, num_items))

    @abc.abstractmethod
    def generate(self, rows: int) -> ColumnData:
        pass


class AgeColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a person's age."""
    min_value = 0
    max_value = 100

    def __init__(self) -> None:
        names = ["age"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        values = self._sample_and_sort(range(self.min_value, self.max_value), rows)
        data = [str(value) for value in values]
        return self._generate_from_data(data)


class DateColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a date."""
    min_value = round(datetime.datetime(year=1970, month=1, day=1).timestamp())
    max_value = round(datetime.datetime(year=1999, month=12, day=31).timestamp())
    max_range = round(datetime.timedelta(days=365 * 2).total_seconds())

    def __init__(self) -> None:
        names = ["date", "start_date", "end_date"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        start = random.randrange(self.min_value, self.max_value - self.max_range)
        end = start + self.max_range
        values = self._sample_and_sort(range(start, end), rows)
        data = [datetime.date.fromtimestamp(value).isoformat() for value in values]
        return self._generate_from_data(data)


class PriceColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a price."""
    min_value = 10
    max_value = 1000

    def __init__(self) -> None:
        names = ["price", "cost", "revenue", "profit", "valuation"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        int_values = self._sample_and_sort(range(self.min_value * 100, self.max_value * 100), rows)
        values = [integer / 100 for integer in int_values]
        data = ["${0:.2f}".format(value) for value in values]
        return self._generate_from_data(data)


class PostalCodeColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a postal code."""
    min_value = 0
    max_value = 99999

    def __init__(self) -> None:
        names = ["zip_code", "postal_code", "post_code"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        values = self._sample_and_sort(range(self.min_value, self.max_value), rows)
        data = ["{0:05d}".format(value) for value in values]
        return self._generate_from_data(data)


class TimeColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a time of the day."""
    min_value = 0
    max_value = 60*60*24

    def __init__(self) -> None:
        names = ["time", "start_time", "end_time"]
        super().__init__(names)

    @staticmethod
    def _to_time(seconds: int) -> datetime.time:
        """Convert a number of seconds to a time object."""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return datetime.time(hour=hours, minute=minutes, second=seconds)

    def generate(self, rows: int) -> ColumnData:
        values = self._sample_and_sort(range(self.min_value, self.max_value), rows)
        data = [self._to_time(value).isoformat() for value in values]
        return self._generate_from_data(data)


class NameColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a name."""
    first_names = [
        "Simone", "Carmelo", "Carissa", "Janise", "Breanne", "Wilford", "Elsy", "Daryl", "Milford", "Mira", "Delma",
        "Berry", "Miki", "Emery", "Ruthe", "Gene", "Lenny", "Shela", "Chang", "Rhett", "Cliff", "Dusty", "Vernie",
        "Fran", "Annita", "Jule", "Taren", "Matilda", "Paola", "Omer", "Luigi", "Alise", "Tama", "Paige", "Ferne",
        "Risa", "Odell", "Wan", "Theo", "Irwin",
    ]
    last_names = [
        "Stanton", "Delarosa", "Coker", "Peterman", "Buckner", "Alder", "Whitmore", "Seibert", "Aldrich", "Layman",
        "Dickens", "Redman", "Shrader", "Otero", "Switzer", "Maher", "Passmore", "Nobles", "Wertz", "Piper", "Lim",
        "Larsen", "Battle", "Overton", "Hargrove", "Manzo", "Kirkland", "Damron", "Kowalski", "Gerald", "Gough", "Nix",
        "Hoyle", "Westfall", "Cantrell", "Folse", "Sneed", "Venegas", "Baptiste", "Ziegler",
    ]

    def __init__(self) -> None:
        names = ["name", "full_name"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        random_first_names = take_random_cycle(self.first_names, rows)
        random_last_names = take_random_cycle(self.last_names, rows)

        # Shuffle the names to avoid an obvious repeating cycle.
        random.shuffle(random_first_names)
        random.shuffle(random_last_names)

        data = [" ".join(pair) for pair in zip(random_first_names, random_last_names)]
        data.sort()

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


class PriorityColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing priorities."""
    def __init__(self, max_discrete_values: Optional[int] = None) -> None:
        names = ["priority", "rank", "importance"]
        possible_values = ["low", "medium", "high"]
        super().__init__(names, possible_values, max_discrete_values)
