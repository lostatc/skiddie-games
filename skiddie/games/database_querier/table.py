"""Classes for generating the table.

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
import random
import itertools
from typing import Sequence, List, NamedTuple

from prompt_toolkit.formatted_text import FormattedText

from skiddie.games.database_querier.columns import ColumnData, ColumnGenerator, ContinuousColumnGenerator, \
    DiscreteColumnGenerator, IndexColumnGenerator
from skiddie.games.database_querier.constraints import Constraint, get_valid_constraints

# The ratio of columns that are discrete as opposed to continuous.
from skiddie.utils import format_table

DISCRETE_COLUMN_RATIO = 0.25

Column = NamedTuple("Column", [("data", ColumnData), ("constraint", Constraint)])


class Table:
    """A table consisting of multiple columns of data.

    Attributes:
        num_rows: The number of rows in the table.
        num_columns: The number of columns in the table.
        columns: The data and constraints for each column in the table.
    """
    def __init__(self, rows: int, columns: int) -> None:
        self.num_rows = rows
        self.num_columns = columns
        self.columns = []

    @property
    def overlapping_indices(self) -> Sequence[int]:
        """The sequence of indices that are contained in all constraints.

        If there are no constraints, this return all indices.
        """
        if not self.columns:
            return range(self.num_rows)

        common_indices = set.intersection(
            *(set(column.constraint.indices) for column in self.columns)
        )

        return sorted(list(common_indices))

    @property
    def overlapping_rows(self) -> int:
        """The number of rows that are contained in all constraints."""
        return len(self.overlapping_indices)

    @property
    def remaining_columns(self) -> int:
        """The number of columns that haven't been created yet."""
        return self.num_columns - len(self.columns)

    def format_constraints(self) -> str:
        """Get a string representations of each constraint to display to the user."""
        return "\n".join(column.constraint.format() for column in self.columns)

    def format_table(self) -> str:
        """Get at formatted string representation of the table."""
        index_data = IndexColumnGenerator().generate(self.num_rows)
        column_data = [column.data for column in self.columns]
        column_data.insert(0, index_data)

        data_columns = [data.rows for data in column_data]
        data_rows = list(zip(*data_columns))

        header_row = [tuple(data.name for data in column_data)]

        return format_table(header_row + data_rows)

    def _get_random_generators(self, max_discrete_values: int) -> List[ColumnGenerator]:
        """Return a random ColumnGenerator instance for each column in the table.

        The ratio of discrete columns to continuous columns is controlled by `DISCRETE_COLUMN_RATIO`.

        DiscreteColumnGenerator subclasses will only be repeated once each has been used once. ContinuousColumnGenerator
        subclasses will only be repeated once each has been used once.

        The discrete columns are all put before the continuous columns. The discrete columns need to come first for
        there to be exactly one row that is contained in all constraints.

        Args:
            max_discrete_values: The maximum number of unique discrete values per column.
        """
        # Get all the subclasses of ContinuousColumnGenerator and DiscreteColumnGenerator.
        continuous_instances = [
            subclass() for subclass in ContinuousColumnGenerator.__subclasses__()
        ]
        discrete_instances = [
            subclass(max_discrete_values) for subclass in DiscreteColumnGenerator.__subclasses__()
        ]

        random.shuffle(continuous_instances)
        random.shuffle(discrete_instances)

        continuous_cycle = itertools.cycle(continuous_instances)
        discrete_cycle = itertools.cycle(discrete_instances)

        # Determine how many of each type to get.
        continuous_range = range(round((1 - DISCRETE_COLUMN_RATIO) * self.num_columns))
        discrete_range = range(round(DISCRETE_COLUMN_RATIO * self.num_columns))

        continuous_output = [next(continuous_cycle) for _ in continuous_range]
        discrete_output = [next(discrete_cycle) for _ in discrete_range]

        return discrete_output + continuous_output

    def create_table(self, max_discrete_values: int) -> None:
        """Create a new random table with a constraint for each column.

        This populates `self.column_data` and `self.constraints`.

        Args:
            max_discrete_values: The maximum number of unique discrete values per column.
        """
        self.columns.clear()

        # Choose random column generators.
        column_generators = self._get_random_generators(max_discrete_values)

        # Generate random constraints.
        for column_generator in column_generators:
            # Generate the random data for this column.
            column_data = column_generator.generate(self.num_rows)

            # Generate the number to reduce the number of overlapping rows by. Subtract one to ensure that there is one
            # row left overlapping at the end.
            reduce_amount = round(self.overlapping_rows / self.remaining_columns) - 1

            # Generate a random constraint for this column.
            constraint_class = random.choice(get_valid_constraints(column_generator))
            constraint = constraint_class(column_data, self.overlapping_indices, reduce_amount)

            # Add the column data and its corresponding constraint.
            self.columns.append(Column(column_data, constraint))

        # This is necessary because up until this point, the discrete columns all come before the continuous columns.
        random.shuffle(self.columns)
