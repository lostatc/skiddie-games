"""Functions and classes related to user interfaces and displaying information.

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
import abc
import shutil
import sys
import six
from typing import Sequence, Optional

import pkg_resources
from prompt_toolkit import print_formatted_text, prompt, Application
from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, Float, FormattedTextControl, Window
from prompt_toolkit.validation import Validator

from skiddie.constants import DESCRIPTIONS_DIR


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


def print_correct_message(message: str = "ACCESS GRANTED", style: str = "fg:ansigreen bold") -> None:
    """Print a message indicating that a game has been completed."""
    print_banner(message, style=style)


def print_incorrect_message(message: str = "INCORRECT", style: str = "fg:ansired bold") -> None:
    """Print a message indicating that an incorrect answer has been given."""
    print_banner(message, style=style)


def get_description(file_name: str) -> str:
    """Get the descriptions of a game.

    Args:
        file_name: The name of the text file containing the description relative to INSTRUCTIONS_DIR.
    """
    # This must not use os.path because resource names are not filesystem paths.
    resource_name = "/".join([DESCRIPTIONS_DIR, file_name])
    return pkg_resources.resource_string("skiddie", resource_name).decode("utf-8")


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


def format_duration(seconds: float) -> str:
    """Return a formatted string representing a duration in seconds.

    A duration of 63.29 seconds would be formatted as "1m 3.3s".
    """
    minutes, seconds = divmod(seconds, 60)
    return "{0:.0f}m {1:.1f}s".format(minutes, seconds)


def format_bytes(num_bytes: int, decimal_places: int = 1) -> str:
    """Format a number of bytes as a human-readable string."""
    remaining_bytes = num_bytes
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"]:
        if remaining_bytes < 1024:
            return "{0:.{1}f}{2}".format(remaining_bytes, decimal_places, unit)
        remaining_bytes /= 1024

    return "{0:.{1}f}YiB".format(remaining_bytes, decimal_places, unit)


def format_table(rows: Sequence[Sequence[str]], separator: str = "  ", align_right: bool = False) -> str:
    """Return the given data in a formatted table.

    Args:
        rows: The rows of data to print.
        separator: The string used to separate each column.
        align_right: Align each column to the right instead of to the left.

    Returns:
        The formatted table.
    """
    # Get the length of the longest string in each column.
    column_lengths = [0 for _ in range(len(max(rows, key=len)))]
    for row in rows:
        for i, item in enumerate(row):
            column_lengths[i] = max(len(item), column_lengths[i])

    format_string = "{0:>{1}}" if align_right else "{0:{1}}"

    # Pad and align each row.
    output = "\n".join(
        separator.join(
            format_string.format(item, column_lengths[i])
            for i, item in enumerate(row)
        )
        for row in rows
    )

    return output


def format_table_columns(
        rows: Sequence[Sequence[str]], rows_per_column: int, header: Optional[Sequence[str]] = None, **kwargs) -> str:
    """Return the given data in a formatted table that splits the data across multiple columns.

    This accepts all the same keyword arguments as `format_table`.

    Args:
        header: The data to use as a header for each column. None for no header.
        rows: The rows of data to print.
        rows_per_column: The maximum number of rows for each column.

    Returns:
        The formatted table.
    """
    # Split the single list of rows into a separate list for each column.
    columns = [list(rows[i:i+rows_per_column]) for i in range(0, len(rows), rows_per_column)]

    # Add headers to each column.
    if header:
        for column in columns:
            column.insert(0, header)

    # The first column should be the longest.
    total_rows = len(columns[0])

    # Split the data into columns by combining rows.
    column_data = []
    for i in range(total_rows):
        combined_row = []
        for column in columns:
            try:
                combined_row += column[i]
            except IndexError:
                # This column does not have a row at this index.
                break

        column_data.append(combined_row)

    return format_table(column_data, **kwargs)


class Screen(abc.ABC):
    """A screen in a graphical terminal application.

    Args:
        multi_screen: A reference to the MultiScreenApp containing this instance.

    Attributes:
        multi_screen: A reference to the MultiScreenApp containing this instance.
    """
    def __init__(self, multi_screen: "MultiScreenApp") -> None:
        self.multi_screen = multi_screen

    @abc.abstractmethod
    def get_root_container(self):
        """Get the top-level container for the screen."""


class MultiScreenApp:
    """A graphical terminal application that supports switching between multiple screens.

    Args:
        app: The application instance to use. This should not define a layout.
        default_screen: The screen that shows by default when the application starts.

    Attributes:
        app: The application instance to use.
        current_screen: The currently selected screen.
        _screen_history: A list that keeps track of which screens have been visited.
    """
    def __init__(self, app: Application, default_screen: Screen) -> None:
        self.app = app
        self.current_screen = default_screen
        self._screen_history = [self.current_screen]

        self.app.layout = Layout(container=default_screen.get_root_container())

    def set_screen(self, screen: Screen) -> None:
        """Set the active screen.

        Args:
            screen: The screen to set as active.
        """
        root_container = screen.get_root_container()
        self.app.layout.container = root_container
        self.app.layout.focus(root_container)

        self._screen_history.append(screen)
        self.current_screen = screen

    def set_previous(self) -> None:
        """Set the active screen to the previous screen."""
        self._screen_history.pop()
        self.set_screen(self._screen_history.pop())

    def add_floating_screen(self, screen: Screen) -> None:
        """Add a screen to the layout as a floating window.

        Args:
            screen: The screen to add.
        """
        root_container = screen.get_root_container()
        self.app.layout.container.floats.append(Float(root_container))
        self.app.layout.focus(root_container)

    def clear_floating(self) -> None:
        """Remove all floating windows."""
        self.app.layout.container.floats.clear()
        self.app.layout.focus(self.app.layout.container)

        # Re-generate the root layout in case the floating windows changed anything.
        root_container = self.current_screen.get_root_container()
        self.app.layout.container = root_container
        self.app.layout.focus(root_container)


class SelectableLabel:
    """A selectable text label.

    This is different from the `Button` classs included with prompt_toolkit in that the contents of the button are
    left-aligned and there are no angle brackets framing the text.

    Args:
        text: The text to display in the label.
        handler: The function to call when the label is selected.
    """
    def __init__(self, text: six.text_type, handler=None) -> None:
        self.text = text
        self.handler = handler

        self.control = FormattedTextControl(
            self.text,
            key_bindings=self._get_key_bindings(),
            focusable=True
        )

        def get_style():
            if get_app().layout.has_focus(self):
                return 'class:selectable-label.focused'
            else:
                return 'class:selectable-label'

        self.window = Window(
            self.control,
            style=get_style,
            dont_extend_width=False,
            dont_extend_height=True,
            always_hide_cursor=True,
        )

    def _get_key_bindings(self) -> KeyBindings:
        bindings = KeyBindings()

        @bindings.add(" ")
        @bindings.add("enter")
        def _handle(_):
            if self.handler is not None:
                self.handler()

        return bindings

    def __pt_container__(self):
        return self.window
