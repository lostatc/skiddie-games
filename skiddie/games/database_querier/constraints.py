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
from typing import List

from prompt_toolkit.formatted_text import FormattedText

from skiddie.games.database_querier.columns import ColumnData


class Constraint(abc.ABC):
    """A method of narrowing down which row has been selected.

    Attributes:
        column: The data from the column that this constraint is applied to.
    """
    def __init__(self, column: ColumnData) -> None:
        self.column = column

    @property
    @abc.abstractmethod
    def indexes(self) -> List[int]:
        """The list of indexes that this constraint limits to."""

    @abc.abstractmethod
    def format(self) -> FormattedText:
        """Return a string representation of the constraint to display to the user."""


class ContinuousConstraint(Constraint):
    """A constraint that works on continuous data."""
    @abc.abstractmethod
    def format(self) -> FormattedText:
        pass


class DiscreteConstraint(Constraint):
    """A constraint that works on discrete data."""
    @abc.abstractmethod
    def format(self) -> FormattedText:
        pass


class EqualsConstraint(DiscreteConstraint):
    """The row is equal to this value."""
    def __init__(self, column: ColumnData, value: str) -> None:
        self.value = value
        super().__init__(column)

    @property
    def indexes(self) -> List[int]:
        return [i for i, item in enumerate(self.column.data) if item == self.value]

    def format(self) -> FormattedText:
        text = "{0} == {1}".format(self.column.name, self.value)
        return FormattedText(("", text))


class NotEqualsConstraint(DiscreteConstraint):
    """The row is not equal to this value."""
    def __init__(self, column: ColumnData, value: str) -> None:
        self.value = value
        super().__init__(column)

    @property
    def indexes(self) -> List[int]:
        return [i for i, item in enumerate(self.column.data) if item != self.value]

    def format(self) -> FormattedText:
        text = "{0} != {1}".format(self.column.name, self.value)
        return FormattedText(("", text))


class LessThanConstraint(ContinuousConstraint):
    """The row is less than this value."""
    def __init__(self, column: ColumnData, value: str) -> None:
        self.value = value
        super().__init__(column)

    @property
    def indexes(self) -> List[int]:
        value_index = self.column.data.index(self.value)
        return [i for i in range(self.column.rows) if i < value_index]

    def format(self) -> FormattedText:
        text = "{0} < {1}".format(self.column.name, self.value)
        return FormattedText(("", text))


class GreaterThanConstraint(ContinuousConstraint):
    """The row is greater than this value."""
    def __init__(self, column: ColumnData, value: str) -> None:
        self.value = value
        super().__init__(column)

    @property
    def indexes(self) -> List[int]:
        value_index = self.column.data.index(self.value)
        return [i for i in range(self.column.rows) if i > value_index]

    def format(self) -> FormattedText:
        text = "{0} > {1}".format(self.column.name, self.value)
        return FormattedText(("", text))


class RangeConstraint(ContinuousConstraint):
    """The row is within this range."""
    def __init__(self, column: ColumnData, lower: str, upper: str) -> None:
        self.lower = lower
        self.upper = upper
        super().__init__(column)

    @property
    def indexes(self) -> List[int]:
        lower_index = self.column.data.index(self.lower)
        upper_index = self.column.data.index(self.upper)
        return [i for i in range(self.column.rows) if lower_index < i < upper_index]

    def format(self) -> FormattedText:
        text = "{0} < {1} < {2}".format(self.lower, self.column.name, self.upper)
        return FormattedText(("", text))
