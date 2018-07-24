"""A game about cracking password hashes.

Copyright © 2017 Wren Powell <wrenp@duck.com>

This file is part of crackit.

crackit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

crackit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with crackit.  If not, see <http://www.gnu.org/licenses/>.

The game starts with rows of characters on the screen. The objective is to add
rows of characters until you have a certain number of rows. Rows can only
contain numbers and letters in the range a-f. A character cannot appear more
than once in the same row or column. If a row is entered that does not meet
these criteria, it is cleared.
"""
import random
import textwrap
import readline  # This is not unused. Importing it adds features to input().
from typing import List, Set, Iterable

from crackit.utils import format_banner, clear_line


class CharGrid:
    """Represent a grid of characters.
    
    Attributes:
        valid_chars: The string of characters that are allowed in the grid.
        num_columns: The number of columns in the grid.
        rows: The grid represented as a list of rows. Each row contains a list
            of characters.
    """
    def __init__(self, valid_chars: Iterable, num_columns: int) -> None:
        self.valid_chars = set(valid_chars)
        self.num_columns = num_columns
        self.rows = []
        
    @property
    def columns(self) -> List[List[str]]:
        """The columns of the grid.
        
        Ignore rows which aren't full.
        """
        full_rows = [
            row for row in self.rows if len(row) == self.num_columns]
        return [list(chars) for chars in zip(*full_rows)]
    
    @property
    def unused_row(self) -> List[Set[str]]:
        """The characters that are unused in each row.
        
        Returns:
            A list containing a set of characters for each row.
        """
        return [self.valid_chars - set(chars) for chars in self.rows]

    @property
    def unused_column(self) -> List[Set[str]]:
        """The characters that are unused in each column.
        
        Returns:
            A list containing a set of characters for each column.
        """
        # If not all columns exist, pad the list.
        output = [self.valid_chars - set(chars) for chars in self.columns]
        output += [self.valid_chars] * (self.num_columns - len(output))
        return output
    
    def format(self) -> str:
        """Format the grid as a single string."""
        return "\n".join("".join(row) for row in self.rows)
    
    def is_valid(self) -> bool:
        """The grid is valid.

        Every row is full and there are no repeating characters in any row or
        column.
        """
        for row in self.rows:
            if len(row) != self.num_columns:
                return False
            elif len(set(row)) < len(row):
                return False
            
        for column in self.columns:
            if len(set(column)) < len(column):
                return False
            
        return True
            
        
def create_grid(rows: int, columns: int, valid_chars: str) -> CharGrid:
    """Generate a random grid of characters.
    
    The same character will not appear more than once in any row or column.
    
    Args:
        rows: The number of rows in the grid.
        columns: The number of columns in the grid.
        valid_chars: A string of characters that may be used in the grid.
            
    Returns:
        A CharGrid object representing the grid of characters.
    """
    char_grid = CharGrid(valid_chars, columns)

    while len(char_grid.rows) < rows:
        char_grid.rows.append([])
        row_num = len(char_grid.rows) - 1
        current_row = char_grid.rows[-1]
        
        # These are characters that have been tried and found to not work. 
        # They are stored in this list to prevent the algorithm from 
        # selecting them a second time. 
        invalid_row_chars = [set() for i in range(columns)]
        
        while len(current_row) < columns:
            column_num = len(current_row) - 1
            try:
                # Randomly select a character from the set of characters 
                # that are not in either the current column or row and 
                # haven't already been found to not work. 
                char = random.choice(list((
                    char_grid.unused_column[column_num + 1]
                    & char_grid.unused_row[row_num])
                    - invalid_row_chars[column_num + 1]))
            except IndexError:
                # There are no characters that will work. Backtrack to the
                # previous position in the row and try a different character.
                invalid_row_chars[column_num].add(current_row.pop())
                for chars in invalid_row_chars[column_num+1:]:
                    # When a character changes, the set of invalid 
                    # characters for subsequent positions must be cleared. 
                    chars.clear()
            else:
                current_row.append(char)

    return char_grid


def main(
        valid_chars="0123456789abcdef", prefix_string="0x", columns=8,
        starting_rows=4, rows_to_win=8) -> None:
    """Play the game.

    Args:
        valid_chars: The string of characters that may be used in the grid.
        prefix_string: A string that prefixes every line in the grid.
        columns: The number of columns in the grid.
        starting_rows: The number of rows in the grid when the game starts.
        rows_to_win: The total number of rows that must be in the grid to win
            the game.
    """
    char_grid = create_grid(starting_rows, columns, valid_chars)
    print(textwrap.indent(char_grid.format(), prefix_string))

    while len(char_grid.rows) < rows_to_win:
        user_input = input(prefix_string)
        char_grid.rows.append(user_input)
        if not char_grid.is_valid():
            clear_line()
            char_grid.rows.pop()

    print(format_banner("ACCESS GRANTED", ansi="\x1b[1;32m"))


if __name__ == "__main__":
    main()
