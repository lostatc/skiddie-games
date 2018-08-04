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
from typing import Sequence

from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.validation import Validator
from prompt_toolkit import print_formatted_text, prompt

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
        print(banner)


class LateInit:
    """Raise an exception if the attribute is unset.

    Args:
        message: The message passed to the exception when the value is accessed before it is set.
    """
    def __init__(self, message: str = "this value must not be None") -> None:
        self._value = None
        self._message = message

    def __get__(self, instance, owner):
        if self._value is None:
            raise ValueError(self._message)
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


def bool_prompt(message: str, default: bool = False) -> bool:
    """Prompt the user to answer yes or no.

    This accepts the same arguments as prompt_toolkit.PromptSession.

    Returns:
        The user's choice.
    """
    true_answers = ["y", "yes"]
    false_answers = ["n", "no"]

    validator = Validator.from_callable(
        lambda x: not x or x.lower() in true_answers + false_answers,
        error_message="Answer must be \"yes\" or \"no\"",
        move_cursor_to_end=True,
    )
    answer = prompt(message=message, validator=validator, validate_while_typing=False)

    if answer:
        return answer.lower() in true_answers
    else:
        return default


def print_table(rows: Sequence[Sequence[str]], padding=2, align_right=False) -> None:
    """Print the given data in a formatted table.

    Args:
        rows: The rows of data to print.
        padding: The number of spaces used to separate each column.
        align_right: Align each column to the right instead of to the left.
    """
    # Get the length of the longest string in each column.
    column_lengths = [0 for _ in range(len(max(rows, key=len)))]
    for row in rows:
        for i, item in enumerate(row):
            column_lengths[i] = max(len(item), column_lengths[i])

    format_string = "{0:>{1}}" if align_right else "{0:{1}}"
    padding_string = " "*padding

    # Pad and align each row.
    output = "\n".join(
        padding_string.join(
            format_string.format(item, column_lengths[i])
            for i, item in enumerate(row)
        )
        for row in rows
    )

    print(output)
