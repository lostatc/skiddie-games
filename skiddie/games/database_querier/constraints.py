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
from typing import Sequence, List, Type

from prompt_toolkit.formatted_text import FormattedText

from skiddie.utils.counting import get_random_cycle
from skiddie.games.database_querier.columns import ColumnData, ColumnGenerator, ContinuousColumnGenerator, DiscreteColumnGenerator


def get_valid_constraints(column_generators: List[ColumnGenerator]) -> List[Type["Constraint"]]:
    """Return a list containing a valid Constraint class for each given ColumnGenerator."""
    continuous_cycle = get_random_cycle(ContinuousConstraint.__subclasses__())
    discrete_cycle = get_random_cycle(DiscreteConstraint.__subclasses__())

    constraint_classes = []
    for generator in column_generators:
        if isinstance(generator, ContinuousColumnGenerator):
            constraint_classes.append(next(continuous_cycle))
        elif isinstance(generator, DiscreteColumnGenerator):
            constraint_classes.append(next(discrete_cycle))

    return constraint_classes


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
    def _distance(self, occurrences: int) -> int:
        """Return how close the value with the given number of occurrences will be to `self.reduce_amount`."""
        reduce_amount = len(self.overlapping_indices) - occurrences
        return abs(reduce_amount - self.reduce_amount)

    @abc.abstractmethod
    def format(self) -> FormattedText:
        pass


class EqualConstraint(DiscreteConstraint):
    """The row is equal to this value."""
    @property
    def indices(self) -> Sequence[int]:
        # Get the number of times each value occurs in the overlapping region.
        occurrences_in_overlap = {value: 0 for value in set(self.data.rows)}
        for i in self.overlapping_indices:
            value = self.data.rows[i]
            occurrences_in_overlap[value] += 1

        # Get the value that, if selected, will reduce the number of overlapping rows by the amount that's closest to
        # `self.reduce_amount`. The constraint will apply to all indices that have this value.
        closest_value, _ = min(
            occurrences_in_overlap.items(),
            key=lambda x: self._distance(x[1])
        )

        # Get all the indices at which this value appears.
        output = [i for i, value in enumerate(self.data.rows) if value == closest_value]
        return output

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
        occurrences_in_overlap = {value: 0 for value in set(self.data.rows)}
        for i in self.overlapping_indices:
            value = self.data.rows[i]
            occurrences_in_overlap[value] += 1

        # Get the value that, if selected, will reduce the number of overlapping rows by the amount that's farthest from
        # `self.reduce_amount`. The constraint will apply to all indices that do not have this value.
        closest_value, _ = max(
            occurrences_in_overlap.items(),
            key=lambda x: self._distance(x[1])
        )

        # Get all the indices at which this value does not appear.
        output = [i for i, value in enumerate(self.data.rows) if value != closest_value]
        return output

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

    Attributes:
        _random_source: Generating the `indices` property involves some randomness. The output of this property must be
            deterministic while still allowing for differences between instances of the class. This source of
            randomness can be re-seeded to ensure deterministic output.
        _random_seed: A seed that is set on initialization and is unique for each instance of this class.
    """
    def __init__(self, data: ColumnData, overlapping_indices: Sequence[int], reduce_amount: int) -> None:
        super().__init__(data, overlapping_indices, reduce_amount)
        self._random_seed = time.time()
        self._random_source = random.Random()
        self._random_source.seed(self._random_seed)

    def _seed_random_source(self) -> None:
        """Reset the seed for `self._random_source`."""
        self._random_source.seed(self._random_seed)

    def _get_random_start_index(self, min_index: int, max_index: int) -> int:
        """Get a random value from `self.overlapping_indices` suitable for the start of a range.

        Args:
            min_index: The minimum value for the start index will be the value of `self.overlapping_indices` at this
                index plus 1.
            max_index: The maximum value for the start index will be the value of `self.overlapping_indices` at this
                index.
        """
        if max_index == 0:
            start_index = self.overlapping_indices[0]
        else:
            start_index = self._random_source.randint(
                self.overlapping_indices[min_index] + 1,
                self.overlapping_indices[max_index],
            )

        return start_index

    def _get_random_end_index(self, min_index: int, max_index: int) -> int:
        """Get a random value from `self.overlapping_indices` suitable for the end of a range.

        Args:
            min_index: The minimum value for the end index will be the value of `self.overlapping_indices` at this
                index.
            max_index: The maximum value for the end index will be the value of `self.overlapping_indices` at this
                index minus 1.
        """
        if min_index in [len(self.overlapping_indices)-1, -1]:
            end_index = self.overlapping_indices[len(self.overlapping_indices)-1]
        else:
            end_index = self._random_source.randint(
                self.overlapping_indices[min_index],
                self.overlapping_indices[max_index] - 1,
            )

        return end_index

    @property
    def _start_index(self) -> int:
        """The start index for a range that starts inside the overlapping region."""
        max_index = self.reduce_amount
        min_index = max_index - 1
        return self._get_random_start_index(min_index, max_index)

    @property
    def _end_index(self) -> int:
        """The end index for a range that ends inside the overlapping region."""
        min_index = -(self.reduce_amount+1)
        max_index = min_index + 1
        return self._get_random_end_index(min_index, max_index)

    @abc.abstractmethod
    def format(self) -> str:
        pass


class LessThanConstraint(ContinuousConstraint):
    """The row is less than this value."""
    @property
    def indices(self) -> Sequence[int]:
        self._seed_random_source()
        return range(0, self._end_index+1)

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
        self._seed_random_source()
        return range(self._start_index, self.data.num_rows)

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
        self._seed_random_source()

        def get_range_after():
            """Get a range that starts in the overlapping region and ends after it."""
            start = self._start_index
            # Increase this by one to ensure that this range cannot be smaller than a length of 2.
            end = self._random_source.randrange(self.overlapping_indices[-1] + 1, self.data.num_rows)

            # Add one to account for the fact that `range` doesn't include the end point.
            return range(start, end+1)

        def get_range_before():
            """Get a range that starts before the overlapping region and ends in it."""
            start = self._random_source.randrange(0, self.overlapping_indices[0])
            end = self._end_index
            return range(start, end+1)

        def get_range_inside():
            """Get a range that starts and ends inside the overlapping region."""
            # The range will start between the values of `self.overlapping_indices` at these indices.
            max_start = self._random_source.randint(0, self.reduce_amount)
            min_start = max_start - 1

            # The range will end between the values of `self.overlapping_indices` at these indices.
            min_end = max_start + (len(self.overlapping_indices)-1 - self.reduce_amount)
            max_end = min_end + 1

            # Randomly decide the indexes to start and end the range at.
            start_index = self._get_random_start_index(min_start, max_start)
            end_index = self._get_random_end_index(min_end, max_end)

            output = range(start_index, end_index+1)
            return output

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

        return self._random_source.choice([
            get_range_after(),
            get_range_before(),
            get_range_inside(),
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
