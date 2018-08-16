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
from typing import Type, Sequence

from skiddie.games.database_querier.columns import ColumnData
from skiddie.games.database_querier.constraints import Constraint


class Table:
    """A table consisting of multiple columns of data.

    Attributes:
        rows: The number of rows in the table.
        columns: The number of columns in the table.
        target_index: The index of the row that the user is trying to find.
        constraints: A list of Constraint instances representing the constraints on each column in the table.
    """
    def __init__(self, rows: int, columns: int) -> None:
        self.rows = rows
        self.columns = columns
        self.target_index = random.choice(range(self.rows))
        self.constraints = []

    def _get_overlapping_indices(self) -> Sequence[int]:
        """Return the sequence of indices that are contained in all constraints."""
        common_indices = set.intersection(
            *(set(constraint.indices) for constraint in self.constraints)
        )
        return sorted(list(common_indices))

    def create_constraint(
            self, column: ColumnData, constraint_type: Type[Constraint], reduce_amount: int) -> Constraint:
        """Create a constraint on the given data that satisfies the given conditions.

        Args:
            column: The the data for the column that the constraint is being applied to.
            constraint_type: The type of constraint to apply.
            reduce_amount: The number of rows to reduce the number of overlapped rows by.
        """
        return constraint_type(column, self._get_overlapping_indices(), reduce_amount)
