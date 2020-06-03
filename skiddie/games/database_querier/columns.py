"""Classes for generating random data for the table.

Copyright 2017-2020 Wren Powell <wrenp@duck.com>

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
from typing import List, Optional

from skiddie.utils.counting import (
    take_random_cycle, sample_and_sort, limit_range, sample_decimal_range, sample_partitions,
    local_range)
from skiddie.utils.ui import format_bytes


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

    @abc.abstractmethod
    def generate(self, rows: int) -> ColumnData:
        pass


class QuantityColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a quantity."""
    min_value = 0
    max_value = 1000
    min_range = 100
    max_range = 100

    def __init__(self) -> None:
        names = ["quantity", "amount"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        local_min, local_max = local_range(self.min_value, self.max_value, self.min_range, self.max_range)
        values = sample_and_sort(range(local_min, local_max), rows)
        data = [str(value) for value in values]
        return self._generate_from_data(data)


class DateColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a date."""
    # Windows systems can't handle 1970-01-01.
    min_value = round(datetime.datetime(year=1970, month=1, day=2).timestamp())
    max_value = round(datetime.datetime(year=1999, month=12, day=31).timestamp())
    max_range = round(datetime.timedelta(days=365 * 2).total_seconds())

    def __init__(self) -> None:
        names = ["date", "start_date", "end_date", "enroll_date", "apply_date", "exp_date"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        limited_range = limit_range(self.min_value, self.max_value, self.max_range)
        values = sample_and_sort(limited_range, rows)
        data = [datetime.date.fromtimestamp(value).isoformat() for value in values]
        return self._generate_from_data(data)


class PriceColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a price."""
    min_value = 1
    max_value = 10000
    min_range = 1000
    max_range = 10000

    def __init__(self) -> None:
        names = ["price", "cost", "revenue", "profit", "valuation"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        local_min, local_max = local_range(self.min_value, self.max_value, self.min_range, self.max_range)
        values = sample_decimal_range(local_min, local_max, rows)
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
        values = sample_and_sort(range(self.min_value, self.max_value), rows)
        data = ["{0:05d}".format(value) for value in values]
        return self._generate_from_data(data)


class TimeColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a time of the day."""
    min_value = 0
    max_value = 60 * 60 * 24
    min_range = 60 * 60
    max_range = 60 * 60 * 24

    def __init__(self) -> None:
        names = ["time", "start_time", "end_time", "timestamp"]
        super().__init__(names)

    @staticmethod
    def _to_time(seconds: int) -> datetime.time:
        """Convert a number of seconds to a time object."""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return datetime.time(hour=hours, minute=minutes, second=seconds)

    def generate(self, rows: int) -> ColumnData:
        local_min, local_max = local_range(self.min_value, self.max_value, self.min_range, self.max_range)
        values = sample_and_sort(range(local_min, local_max), rows)
        data = [self._to_time(value).isoformat() for value in values]
        return self._generate_from_data(data)


class NameColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a name."""
    first_names = [
        "Simone", "Carmelo", "Carissa", "Janise", "Breanne", "Wilford", "Elsy", "Daryl", "Milford", "Mira", "Delma",
        "Berry", "Miki", "Emery", "Ruthe", "Gene", "Lenny", "Shela", "Chang", "Rhett", "Cliff", "Dusty", "Vernie",
        "Fran", "Annita", "Jule", "Taren", "Matilda", "Paola", "Omer", "Luigi", "Alise", "Tama", "Paige", "Ferne",
        "Risa", "Odell", "Wan", "Theo", "Irwin", "Hilda", "Janelle", "Jacque", "Luana", "Nelle", "Grover", "Chi",
        "Cleo", "Jarvis", "Esther", "Rory", "Shen", "Oren", "Oliver", "Birch", "Cloud", "Cove", "Ciro",
        "Ferris", "West", "Cedar", "Fen", "Rain", "Vale", "Echo", "Kadin", "Moss", "Milo", "Remus", "Sirius", "Minerva",
        "Severus", "Albus", "Alastor", "Harrier", "Kim", "Evrart", "René", "Titus", "Klassje", "Guillaume"
    ]
    last_names = [
        "Stanton", "Delarosa", "Coker", "Peterman", "Buckner", "Alder", "Whitmore", "Seibert", "Aldrich", "Layman",
        "Dickens", "Redman", "Shrader", "Otero", "Switzer", "Maher", "Passmore", "Nobles", "Wertz", "Piper", "Lim",
        "Larsen", "Battle", "Overton", "Hargrove", "Manzo", "Kirkland", "Damron", "Kowalski", "Gerald", "Gough", "Nix",
        "Hoyle", "Westfall", "Cantrell", "Folse", "Sneed", "Venegas", "Baptiste", "Ziegler", "Horvath", "Hogan",
        "Kinchloe", "Carter", "LeBeau", "Newkirk", "Klink", "Schultz", "Burkhalter", "Hochstetter", "Haden", "Oshiro",
        "Du Bois", "Kitsuragi", "Hardie", "Garte", "Vicquemare",
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


class BytesColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a number of bytes."""
    min_value = 1024**1  # 1 KiB
    max_value = 1024**4  # 1 TiB

    def __init__(self) -> None:
        names = ["bytes", "size", "capacity", "space", "storage"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        values = sample_partitions(
            self.min_value, self.max_value, rows, decimal_places=0, partition_magnitude=3
        )
        data = [format_bytes(value) for value in values]
        return self._generate_from_data(data)


class LatLongGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a latitude or longitude"""
    min_value = -90
    max_value = 90
    min_range = 30
    max_range = 180

    def __init__(self) -> None:
        names = ["latitude", "longitude"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        local_min, local_max = local_range(self.min_value, self.max_value, self.min_range, self.max_range)
        values = sample_decimal_range(local_min, local_max, rows, decimal_places=4)
        data = ["{0:.4f}".format(value) for value in values]
        return self._generate_from_data(data)


class DurationColumnGenerator(ContinuousColumnGenerator):
    """A continuous data type representing a duration in seconds."""
    min_value = 100
    max_value = 100000000

    def __init__(self) -> None:
        names = ["duration", "seconds", "elapsed_time"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        values = sample_partitions(self.min_value, self.max_value, rows, decimal_places=0)
        data = ["{0:.4e}".format(value) for value in values]
        return self._generate_from_data(data)


class IDColumn(ContinuousColumnGenerator):
    """A continuous data type representing a unique id."""
    min_value = 0x00000000
    max_value = 0xffffffff

    def __init__(self) -> None:
        names = ["id", "key"]
        super().__init__(names)

    def generate(self, rows: int) -> ColumnData:
        values = sample_and_sort(range(self.min_value, self.max_value), rows)
        data = ["{0:08x}".format(value) for value in values]
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
    """A discrete data type representing a boolean value."""
    def __init__(self) -> None:
        names = ["exists", "preferred", "enabled", "open", "active"]
        possible_values = ["true", "false"]
        super().__init__(names, possible_values, max_discrete_values=2)


class ActivityColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing a status."""

    def __init__(self) -> None:
        names = ["activity", "activity_status"]
        possible_values = ["active", "inactive", "standby"]
        super().__init__(names, possible_values, max_discrete_values=2)


class SpecializationColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing a specialization."""
    def __init__(self) -> None:
        names = ["level", "precedence"]
        possible_values = ["primary", "secondary", "tertiary"]
        super().__init__(names, possible_values, max_discrete_values=2)


class VisibilityColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing a visibility."""

    def __init__(self) -> None:
        names = ["visibility"]
        possible_values = ["public", "private", "protected"]
        super().__init__(names, possible_values, max_discrete_values=2)


class ProcessStateColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing the state of a process."""

    def __init__(self) -> None:
        names = ["process_state", "task_state", "job_state", "transaction_state"]
        possible_values = ["working", "failed", "complete", "waiting"]
        super().__init__(names, possible_values, max_discrete_values=2)


class TestStateColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing the state of a test suite."""

    def __init__(self) -> None:
        names = ["tests", "build"]
        possible_values = ["passing", "failing"]
        super().__init__(names, possible_values, max_discrete_values=2)


class ShippingStatusColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing the shipping status of a delivery."""

    def __init__(self) -> None:
        names = ["shipping_status"]
        possible_values = ["shipped", "en_route", "delivered"]
        super().__init__(names, possible_values, max_discrete_values=2)


class PriorityColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing a priority."""

    def __init__(self) -> None:
        names = ["priority"]
        possible_values = ["low", "medium", "high", "immediate"]
        super().__init__(names, possible_values, max_discrete_values=3)


class ConditionColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing a condition."""
    def __init__(self) -> None:
        names = ["condition"]
        possible_values = ["poor", "moderate", "good", "great"]
        super().__init__(names, possible_values, max_discrete_values=3)


class SeverityColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing a severity level."""
    def __init__(self) -> None:
        names = ["severity", "importance"]
        possible_values = ["minor", "normal", "major", "critical"]
        super().__init__(names, possible_values, max_discrete_values=3)


class MachineStateColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing the state of a machine."""
    def __init__(self) -> None:
        names = ["machine_state"]
        possible_values = ["running", "power_off", "sleeping", "hibernating"]
        super().__init__(names, possible_values, max_discrete_values=3)


class SizeColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing a size."""

    def __init__(self) -> None:
        names = ["size"]
        possible_values = ["tiny", "small", "medium", "large", "xlarge"]
        super().__init__(names, possible_values, max_discrete_values=3)


class ReleaseColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type representing the release stage of a project."""

    def __init__(self) -> None:
        names = ["release_stage", "release_state"]
        possible_values = ["alpha", "beta", "testing", "candidate", "release", "stable"]
        super().__init__(names, possible_values, max_discrete_values=3)


class WorkStatusColumnGenerator(DiscreteColumnGenerator):
    """A discrete data type represeinting the status of a worker."""

    def __init__(self) -> None:
        names = ["work_status", "worker_status"]
        possible_values = ["on_site", "remote", "sick", "leave", "vacation"]
        super().__init__(names, possible_values, max_discrete_values=3)
