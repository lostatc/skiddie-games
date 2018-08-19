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
from typing import Sequence, List, NamedTuple

from prompt_toolkit.formatted_text import FormattedText

from skiddie.games.database_querier.columns import (
    ColumnData, ColumnGenerator, ContinuousColumnGenerator, DiscreteColumnGenerator,
)
from skiddie.games.database_querier.constraints import Constraint, get_valid_constraints
from skiddie.utils.ui import format_table
from skiddie.utils.counting import take_random_cycle

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

    def format_constraints(self, separator: str = "\n") -> FormattedText:
        """Get a formatted text representation of all the constraints to display to the user."""
        style_tuples = []

        for column in self.columns:
            style_tuples += column.constraint.format().data
            style_tuples += [("", separator)]

        # Remove the trailing separator.
        style_tuples.pop()

        return FormattedText(style_tuples)

    def format_table(self) -> str:
        """Get at formatted string representation of the table."""
        data_columns = [column.data.rows for column in self.columns]
        data_rows = list(zip(*data_columns))

        header_row = [tuple(data.data.name for data in self.columns)]

        return format_table(header_row + data_rows)

    def _get_random_generators(self) -> List[ColumnGenerator]:
        """Return a random ColumnGenerator instance for each column in the table.

        The ratio of discrete columns to continuous columns is controlled by `DISCRETE_COLUMN_RATIO`.

        DiscreteColumnGenerator subclasses will only be repeated once each has been used once. ContinuousColumnGenerator
        subclasses will only be repeated once each has been used once.

        The discrete columns are all put before the continuous columns. The discrete columns need to come first for
        there to be exactly one row that is contained in all constraints.
        """
        # Get all the subclasses of ContinuousColumnGenerator and DiscreteColumnGenerator.
        continuous_instances = [
            subclass() for subclass in ContinuousColumnGenerator.__subclasses__()
        ]
        discrete_instances = [
            subclass() for subclass in DiscreteColumnGenerator.__subclasses__()
        ]

        # Determine how many of each type to get.
        continuous_items = round((1 - DISCRETE_COLUMN_RATIO) * self.num_columns)
        discrete_items = round(DISCRETE_COLUMN_RATIO * self.num_columns)

        # Randomly select subclasses.
        continuous_output = take_random_cycle(continuous_instances, continuous_items)
        discrete_output = take_random_cycle(discrete_instances, discrete_items)

        return discrete_output + continuous_output

    def create_table(self) -> None:
        """Create a new random table with a constraint for each column.

        This populates `self.column_data` and `self.constraints`.
        """
        self.columns.clear()

        # Choose random column generators.
        column_generators = self._get_random_generators()

        # Choose random constraint classes.
        constraint_classes = get_valid_constraints(column_generators)

        # Generate random constraints.
        for column_generator, constraint_class in zip(column_generators, constraint_classes):
            # Generate the random data for this column.
            column_data = column_generator.generate(self.num_rows)

            # Generate the number to reduce the number of overlapping rows by. Subtract one to ensure that there is one
            # row left overlapping at the end.
            reduce_amount = round(self.overlapping_rows / self.remaining_columns) - 1

            # Generate a constraint for this column.
            constraint = constraint_class(column_data, self.overlapping_indices, reduce_amount)

            # Add the column data and its corresponding constraint.
            self.columns.append(Column(column_data, constraint))

        # This is necessary because up until this point, the discrete columns all come before the continuous columns.
        random.shuffle(self.columns)
