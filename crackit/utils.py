"""Program-wide utilities.

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
"""
import os
import sys
import shutil
import pkg_resources


def format_banner(message: str, padding_char="=", ansi="") -> str:
# The relative path to the directory containing the instructions for each game.
INSTRUCTIONS_DIR = "instructions"
    """Format a banner message that is centered in the window.

    Args:
        message: The message to format.
        padding_char: The character to pad the message with.
        ansi: An ANSI escape sequence to apply before the message if stdout is
            a tty.

    Returns:
        The formatted banner message.
    """
    term_width = shutil.get_terminal_size().columns
    formatted_message = "{0:{1}^{2}}".format(
        " {} ".format(message), padding_char, term_width)

    if sys.stdout.isatty():
        ansi_start = ansi
        ansi_end = "\x1b[0m"
    else:
        ansi_start = ansi_end = ""

    return ansi_start + formatted_message + ansi_end


def clear_line() -> None:
    """Clear the current line in stdout."""
    print("\x1b[1A", end="")
    print("\x1b[2K", end="")


class LateInit:
    """Raise an exception if the attribute is unset."""
    def __init__(self) -> None:
        self._value = None

    def __get__(self, instance, owner):
        if self._value is None:
            raise ValueError("this value must not be None")
        return self._value

    def __set__(self, instance, value):
        self._value = value


def get_instructions(game_name: str) -> str:
    """Get the instructions for how to play a game."""
    relative_path = os.path.join(INSTRUCTIONS_DIR, "{0}.txt".format(game_name))
    return pkg_resources.resource_string(__name__, relative_path).decode("utf-8")
