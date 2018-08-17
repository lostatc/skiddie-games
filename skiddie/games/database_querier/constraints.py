"""Classes for narrowing down which row has been selected.

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
import time
import collections
from typing import Sequence, List, Type

from prompt_toolkit.formatted_text import FormattedText

from skiddie.games.database_querier.columns import ColumnData, ColumnGenerator, ContinuousColumnGenerator, DiscreteColumnGenerator


def get_valid_constraints(column: ColumnGenerator) -> List[Type["Constraint"]]:
    """Return a list of constraint types that can be used with this type of column."""
    if isinstance(column, ContinuousColumnGenerator):
        return ContinuousConstraint.__subclasses__()
    if isinstance(column, DiscreteColumnGenerator):
        return DiscreteConstraint.__subclasses__()


class Constraint(abc.ABC):
    """A method of narrowing down which row is the solution.

    Each column in the table has a constraint applied to it. These constraints, through the `indices` property, each
    give a possible range of rows that the solution can be in. When the constraints for each column overlap, there will
    only be one row which is contained in each constraint. That row is the solution.

    Attributes:
        data: The data from the column that this constraint is applied to.
        overlapping_indices: The indices of all the rows that are overlapping with other constraints.
        reduce_amount: The number of rows to reduce the number of overlapped rows by. The number of rows contained in
            both `overlapping_indices` and `indices` will be less than the number contained in just
            `overlapping_indices` by this amount.

    """
    def __init__(self, data: ColumnData, overlapping_indices: Sequence[int], reduce_amount: int) -> None:
        if reduce_amount > len(overlapping_indices):
            raise ValueError("`reduce_amount` cannot exceed the size of `overlapping_indices`")

        self.data = data
        self.overlapping_indices = overlapping_indices
        self.reduce_amount = reduce_amount

    @property
    @abc.abstractmethod
    def indices(self) -> Sequence[int]:
        """The sequence of indices that are in this constraint."""

    @abc.abstractmethod
    def format(self) -> FormattedText:
        """Return a string representation of the constraint to display to the user."""


class DiscreteConstraint(Constraint):
    """A constraint that works on discrete data.

    DiscreteConstraint subclasses may not be able to reduce the number of overlapping rows by exactly
    `self.reduce_amount`. They will choose the `indices` that come the closest.
    """
    @abc.abstractmethod
    def format(self) -> FormattedText:
        pass


class EqualConstraint(DiscreteConstraint):
    """The row is equal to this value."""
    @property
    def indices(self) -> Sequence[int]:
        # Get the number of times each value occurs in the overlapping region.
        occurrences_in_overlap = collections.defaultdict(lambda: 0)
        for i in self.overlapping_indices:
            value = self.data.rows[i]
            occurrences_in_overlap[value] += 1

        # Get the value with the number of occurrences that's farthest from `self.reduce_amount`. The constraint will
        # apply to all indices that have this value.
        closest_value, _ = max(
            occurrences_in_overlap.items(),
            key=lambda x: abs(x[1] - self.reduce_amount)
        )

        # Get all the indices at which this value appears.
        return [i for i, value in enumerate(self.data.rows) if value == closest_value]

    def format(self) -> FormattedText:
        # Get the first index that is in `self.indices`.
        first_index = self.indices[0]
        style_tuples = [
            ("class:column-name", self.data.name),
            ("", " == {0}".format(self.data.rows[first_index])),
        ]
        return FormattedText(style_tuples)


class NotEqualConstraint(DiscreteConstraint):
    """The row is not equal to this value."""
    @property
    def indices(self) -> Sequence[int]:
        # Get the number of times each value occurs in the overlapping region.
        occurrences_in_overlap = collections.defaultdict(lambda: 0)
        for i in self.overlapping_indices:
            value = self.data.rows[i]
            occurrences_in_overlap[value] += 1

        # Get the value with the number of occurrences that's closest to `self.reduce_amount`. The constraint will
        # apply to all indices that do not have this value.
        closest_value, _ = min(
            occurrences_in_overlap.items(),
            key=lambda x: abs(x[1] - self.reduce_amount)
        )

        # Get all the indices at which this value does not appear.
        return [i for i, value in enumerate(self.data.rows) if value != closest_value]

    def format(self) -> FormattedText:
        # Get the first index that is not in `self.indices`.
        first_index = next(i for i in range(self.data.num_rows) if i not in self.indices)
        style_tuples = [
            ("class:column-name", self.data.name),
            ("", " != {0}".format(self.data.rows[first_index])),
        ]
        return FormattedText(style_tuples)


class ContinuousConstraint(Constraint):
    """A constraint that works on continuous data.

    ContinuousConstraint subclasses will always be able to reduce the number of overlapping rows by exactly
    `self.reduce_amount`.
    """
    @abc.abstractmethod
    def format(self) -> str:
        pass


class LessThanConstraint(ContinuousConstraint):
    """The row is less than this value."""
    @property
    def indices(self) -> Sequence[int]:
        return range(0, self.overlapping_indices[-self.reduce_amount])

    def format(self) -> FormattedText:
        highest_index = self.indices[-1]
        style_tuples = [
            ("class:column-name", self.data.name),
            ("", " <= {0}".format(self.data.rows[highest_index])),
        ]
        return FormattedText(style_tuples)


class GreaterThanConstraint(ContinuousConstraint):
    """The row is greater than this value."""
    @property
    def indices(self) -> Sequence[int]:
        return range(self.overlapping_indices[self.reduce_amount], self.data.num_rows)

    def format(self) -> FormattedText:
        lowest_index = self.indices[0]
        style_tuples = [
            ("class:column-name", self.data.name),
            ("", " >= {0}".format(self.data.rows[lowest_index])),
        ]
        return FormattedText(style_tuples)


class RangeConstraint(ContinuousConstraint):
    """The row is within this range.

    Attributes:
        _random_seed: Generating the `indices` property involves some randomness. The output of this property must be
            deterministic, while still allowing for differences between instances of the class. This number is set on
            initialization and is used to seed the random number generator each time the property is called.
    """
    def __init__(self, data: ColumnData, overlapping_indices: Sequence[int], reduce_amount: int) -> None:
        self._random_seed = time.time()
        super().__init__(data, overlapping_indices, reduce_amount)

    @property
    def indices(self) -> Sequence[int]:
        random_source = random.Random()
        random_source.seed(self._random_seed)

        def get_range_after():
            """Get a range that starts in the overlapping region and ends after it."""
            start = self.overlapping_indices[self.reduce_amount]
            # Increase this by one to ensure that this range cannot be smaller than a length of 2.
            end = random_source.randrange(self.overlapping_indices[-1] + 1, self.data.num_rows)

            # Add one to account for the fact that `range` doesn't include the end point.
            return range(start, end + 1)

        def get_range_before():
            """Get a range that starts before the overlapping region and ends in it."""
            start = random_source.randrange(0, self.overlapping_indices[0])
            end = self.overlapping_indices[-self.reduce_amount]
            return range(start, end)

        def get_range_inside():
            """Get a range that starts and ends inside the overlapping region."""
            range_size = self.data.num_rows - self.reduce_amount
            start = random_source.randrange(0, self.data.num_rows - range_size)
            end = start + range_size
            return range(start, end)

        at_start = self.overlapping_indices[0] == 0
        at_end = self.overlapping_indices[-1] + 1 == self.data.num_rows

        if at_start and at_end:
            # The overlapping region covers the entire column, so the range cannot start before it or end after it.
            return get_range_inside()
        if at_start:
            # The overlapping region starts at the beginning of the column, so the range cannot start before it.
            return get_range_after()
        if at_end:
            # The overlapping region ends at the end of the column, so the range cannot end after it.
            return get_range_before()

        return random_source.choice([
            get_range_after(),
            get_range_before(),
        ])

    def format(self) -> FormattedText:
        lowest_index = self.indices[0]
        highest_index = self.indices[-1]
        style_tuples = [
            ("", "{0} <= ".format(self.data.rows[lowest_index])),
            ("class:column-name", self.data.name),
            ("", " <= {0}".format(self.data.rows[highest_index])),
        ]
        return FormattedText(style_tuples)
