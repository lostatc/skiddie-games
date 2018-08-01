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

from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import print_formatted_text

# The relative path to the directory containing the instructions for each game.
INSTRUCTIONS_DIR = "descriptions"


def _format_banner(message: str, padding_char="=") -> str:
    """Format a banner message that is centered in the window.

    Args:
        message: The message to format.
        padding_char: The character to pad the message with.

    Returns:
        The formatted banner message.
    """
    term_width = shutil.get_terminal_size().columns
    return "{0:{1}^{2}}".format(" {} ".format(message), padding_char, term_width)


def print_banner(message: str, padding_char: str = "=", style: str = "") -> None:
    """Print a banner message that is centered in the window.

    Args:
        message: The message to print.
        padding_char: The character to pad the message with.
        style: A space-separated string of styles to apply to the message.
    """
    banner = _format_banner(message, padding_char)

    if sys.stdout.isatty():
        print_formatted_text(FormattedText([(style, banner)]))
    else:
        print_formatted_text(banner)


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


def get_description(file_name: str) -> str:
    """Get the descriptions of a game.

    Args:
        file_name: The name of the text file containing the description relative to INSTRUCTIONS_DIR.
    """
    relative_path = os.path.join(INSTRUCTIONS_DIR, file_name)
    return pkg_resources.resource_string(__name__, relative_path).decode("utf-8")


def format_duration(seconds: float) -> str:
    """Return a formatted string representing a duration in seconds.

    A duration of 63.29 seconds would be formatted as "1m 3.3s".
    """
    minutes, seconds = divmod(seconds, 60)
    return "{0:.0f}m {1:.1f}s".format(minutes, seconds)

