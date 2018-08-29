"""Code for generating patterns.

Copyright © 2017-2018 Wren Powell <wrenp@duck.com>

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
from typing import List

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText


class PatternGrid:
    """A grid of cells that are either on or off.

    Attributes:
        grid: A list of rows, each of which is a list of cells.
    """
    def __init__(self, grid: List[List[bool]]) -> None:
        self.grid = grid

    @property
    def width(self) -> int:
        """The number of columns in the grid."""
        return len(max(self.grid, key=len))

    @property
    def height(self) -> int:
        """The number of rows in the grid."""
        return len(self.grid)

    def scramble(self, cells_to_flip: int) -> None:
        """Randomly flip the state of cells in this grid.

        Args:
            cells_to_flip: The number of cells to flip.
        """
        for _ in range(cells_to_flip):
            row = random.choice(range(self.height))
            column = random.choice(range(self.width))
            self.grid[row][column] = not self.grid[row][column]

    def format_grid(
            self,
            on_string: str = "  ", on_style: str = "reverse",
            off_string: str = "  ", off_style: str = "") -> FormattedText:
        """Format the grid as a string.

        Args:
            on_string: The string to display for cells that are on.
            on_style: The style to apply to cells that are on.
            off_string: The string to display for cells that are off
            off_style: The style to apply to cells that are off.
        """
        style_pairs = []

        for row in self.grid:
            for cell in row:
                style_pairs.append((
                    on_style if cell else off_style,
                    on_string if cell else off_string,
                ))

            style_pairs.append(("", "\n"))

        # Remove the trailing newline.
        style_pairs.pop()

        return FormattedText(style_pairs)

    def check_negative(self, other: "PatternGrid") -> bool:
        """Returns whether the given pattern grid is a negative of this one."""
        return self.create_negative(other).grid == self.grid

    @classmethod
    def create_random(cls, width: int, height: int, coverage: float) -> "PatternGrid":
        """Create a new random grid.

        Args:
            width: The number of column in the grid.
            height: The number of rows in the grid.
            coverage: The proportion of cells that are turned on.
        """
        grid = [
            [random.random() < coverage for _ in range(width)]
            for _ in range(height)
        ]

        return cls(grid)

    @classmethod
    def create_negative(cls, template: "PatternGrid") -> "PatternGrid":
        """Create a new grid that is the negative pattern of the given grid."""
        grid = [
            [not cell for cell in row]
            for row in template.grid
        ]

        return cls(grid)
