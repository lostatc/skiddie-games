"""A game about cracking password hashes.

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
import random
from typing import List, Set, Iterable

from prompt_toolkit.validation import Validator
from prompt_toolkit import PromptSession

from skiddie.constants import GUI_STYLE
from skiddie.utils.ui import print_correct_message

# The string that prefixes every line in the grid.
PREFIX_STRING = "0x"

# The string of characters that may be used in the grid.
VALID_CHARS = "0123456789abcdef"

# A list of possible usernames to be used for formatting the output.
USERNAMES = [
    "lostatc", "root", "daemon", "bin", "sys", "sync", "games", "man", "mail", "news", "uucp", "proxy", "www-data",
    "backup", "list",  "irc", "nobody", "systemd-network", "systemd-resolve", "syslog", "messagebus", "uuidd", "usbmux",
    "dnsmasq", "rtkit", "saned", "pulse", "avahi", "colord", "gdm", "libvirt-qemu", "chrony", "lp", "nscd", "polkitd",
    "postfix", "sshd", "mysql", "svn", "redis", "statd", "rpc", "kernoops",
]


class CharGrid:
    """Represent a grid of characters.

    Attributes:
        valid_chars: The string of characters that are allowed in the grid.
        num_columns: The number of columns in the grid.
        rows: The grid represented as a list of rows. Each row contains a list of characters.
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
        full_rows = [row for row in self.rows if len(row) == self.num_columns]
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

        Every row is full and there are no repeating characters in any row or column.
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

    def check_row(self, row: str) -> bool:
        """Return whether the given row would be valid if added to the grid."""
        self.rows.append(row)
        if not self.is_valid():
            self.rows.pop()
            return False
        return True


def create_grid(rows: int, columns: int, valid_chars: str = VALID_CHARS) -> CharGrid:
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

        # These are characters that have been tried and found to not work. They are stored in this list to prevent the
        # algorithm from selecting them a second time.
        invalid_row_chars = [set() for _ in range(columns)]

        while len(current_row) < columns:
            column_num = len(current_row) - 1
            try:
                # Randomly select a character from the set of characters that are not in either the current column or
                # row and haven't already been found to not work.
                char = random.choice(list(
                    (char_grid.unused_column[column_num + 1] & char_grid.unused_row[row_num])
                    - invalid_row_chars[column_num + 1]
                ))
            except IndexError:
                # There are no characters that will work. Backtrack to the previous position in the row and try a
                # different character.
                invalid_row_chars[column_num].add(current_row.pop())
                for chars in invalid_row_chars[column_num+1:]:
                    # When a character changes, the set of invalid characters for subsequent positions must be cleared.
                    chars.clear()
            else:
                current_row.append(char)

    return char_grid


def format_line(username: str, pad_width: int, hex_string: str) -> str:
    """Format a line of output stylized as a /etc/passwd file.

    Args:
        username: The username to display on this line.
        pad_width: The length of the longest username that will appear.
        hex_string: The password hash.

    Returns:
        The formatted string.
    """
    return "{0:>{1}}:  {2}{3}".format(
        username,
        pad_width,
        PREFIX_STRING,
        hex_string,
    )


def play(rows_to_win: int, starting_rows: int, columns: int) -> None:
    """Play the game.

    Args:
        columns: The number of columns in the grid. Increasing this makes the game more difficult.
        starting_rows: The number of rows in the grid when the game starts. Increasing this makes the game more
            difficult.
        rows_to_win: The total number of rows that must be in the grid to win the game. Increasing this makes the game
            more difficult.
    """
    char_grid = create_grid(starting_rows, columns)
    usernames = random.sample(USERNAMES, rows_to_win)
    pad_width = len(max(usernames, key=len))

    # Format and print the initial grid.
    starting_grid = "\n".join(
        format_line(usernames.pop(), pad_width, line)
        for line in char_grid.format().splitlines()
    )
    print(starting_grid)

    # Create the prompt session.
    validator = Validator.from_callable(char_grid.check_row, error_message="Invalid row", move_cursor_to_end=True)
    session = PromptSession(validator=validator, validate_while_typing=False, mouse_support=True, style=GUI_STYLE)

    # Prompt the user until they complete enough lines.
    while len(char_grid.rows) < rows_to_win:
        session.prompt(format_line(usernames.pop(), pad_width, ""))

    print_correct_message()
