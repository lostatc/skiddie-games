"""The main function for the game.

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
import random

from prompt_toolkit.validation import Validator
from prompt_toolkit import PromptSession

from crackit.utils import print_banner
from crackit.constants import GUI_STYLE
from crackit.games.shell_scripter.command import Command
from crackit.games.shell_scripter.constants import INPUT_FILE_NAMES, OUTPUT_FILE_NAMES, COMMANDS

# The string that is printed before each command and line of user input.
COMMAND_PROMPT = "$ "


def play(
        commands_to_win: int, min_args: int, max_args: int,
        redirect_probability: float, pipe_probability: float) -> None:
    """Play the game.

    Args:
        commands_to_win: The number of commands that must be correctly entered to win the game.
        min_args: The minimum number of non-required arguments that a command can have.
        max_args: The maximum number of non-required arguments that a command can have.
        redirect_probability: The probability that a command will send its output to a pipe or file.
        pipe_probability: The probability that a command will use a pipe when redirecting its output.
    """
    # Set class attributes that determine how commands are generated.
    Command.min_args = min_args
    Command.max_args = max_args
    Command.redirect_probability = redirect_probability
    Command.pipe_probability = pipe_probability
    Command.input_names = INPUT_FILE_NAMES
    Command.output_names = OUTPUT_FILE_NAMES

    session = PromptSession(validate_while_typing=False, mouse_support=True, style=GUI_STYLE)

    # Print random commands and prompt the user to type them in until they type them in correctly.
    for _ in range(commands_to_win):
        command_string = random.choice(COMMANDS).get_random()
        print(COMMAND_PROMPT + command_string)

        validator = Validator.from_callable(
            lambda x: x == command_string, error_message="Commands do not match", move_cursor_to_end=True)
        session.prompt(COMMAND_PROMPT, validator=validator)

        print()

    print_banner("ACCESS GRANTED", style="ansigreen bold")
