"""Code for generating random commands.

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


class Argument:
    """An argument to a shell command.

    Attributes:
        names: A list of possible names for the argument.
        values: A list of possible values for the argument.
    """
    def __init__(self, names: List[str], values: List[str]) -> None:
        self.names = names
        self.values = values

    def get_random(self) -> str:
        """Generate a random argument within the given constraints as a string.

        Returns:
            The argument as a string.
        """
        # Don't print the separator if either the list of names or list of values are empty.
        return " ".join(random.choice(choices) for choices in (self.names, self.values) if choices)


class Command:
    """A shell command that the user can be prompted to type.

    Attributes:
        name: The name of the command.
        positional_args: A list of required positional arguments for the command. Each command in this list is used once
            in the order that it appears.
        optional_args: A list of optional arguments for the command. Commands in this list are chosen randomly and can
            be used in any order.
        redirect_output: The command can redirect its output.
        redirect_input: The command must redirect its input.
    """
    def __init__(
            self, name: str, positional_args: List[Argument], optional_args: List[Argument],
            redirect_output: bool = False, redirect_input: bool = False) -> None:
        self.name = name
        self.positional_args = positional_args
        self.optional_args = optional_args
        self.redirect_output = redirect_output
        self.redirect_input = redirect_input


class CommandGenerator:
    """A class that generates random command strings.

    Attributes:
        commands: The commands to choose from.
        input_names: The names of files used as sources of input.
        output_names: The names of files used to redirect output.
        min_args: The minimum number of non-required arguments that a command can have.
        max_args: The maximum number of non-required arguments that a command can have.
        redirect_probability: The probability that a command will send its output to a pipe or file.
        pipe_probability: The probability that a command will use a pipe when redirecting its output.
    """
    def __init__(
            self, commands: List[Command], input_names: List[str], output_names: List[str],
            min_args: int, max_args: int, redirect_probability: float, pipe_probability: float) -> None:
        self.commands = commands
        self.input_names = input_names
        self.output_names = output_names
        self.min_args = min_args
        self.max_args = max_args
        self.redirect_probability = redirect_probability
        self.pipe_probability = pipe_probability

    def get_random(
            self, redirect_input: bool = True, redirect_output: bool = True,
            supports_input: bool = True, supports_output: bool = True) -> str:
        """Generate a random command string within the given constraints.

        Args:
            redirect_input: Have a chance of adding random input redirection to the command string.
            redirect_output: Have a chance of adding random output redirection to the command string.
            supports_input: Only return a command that supports input redirection.
            supports_output: Only return a command that supports output redirection.

        Returns:
            The command as a string.
        """
        available_commands = [
            command for command in self.commands
            if command.redirect_input == supports_input and command.redirect_output == supports_output
        ]
        command = random.choice(available_commands)

        selected_args = command.positional_args.copy()
        remaining_args = command.optional_args.copy()

        # Select random parameters.
        if self.max_args == 0:
            number_of_args = 0
        else:
            number_of_args = random.randrange(self.min_args, self.max_args)

        # Add a random number of optional arguments.
        random.shuffle(remaining_args)
        for _ in range(number_of_args):
            try:
                selected_args.append(remaining_args.pop())
            except IndexError:
                break

        # Generate a command string.
        if not selected_args:
            command_string = command.name
        else:
            command_string = "{0} {1}".format(command.name, " ".join(arg.get_random() for arg in selected_args))

        # Add random redirects to the command string.
        if command.redirect_input and redirect_input:
            command_string = self._add_input_redirection(command_string)
        if command.redirect_output and redirect_output and random.random() < self.redirect_probability:
            command_string = self._add_output_redirection(command_string)

        return command_string

    def _add_input_redirection(self, command_string: str) -> str:
        """Add random input redirection to the given command string."""
        if random.random() < self.pipe_probability:
            return "{0} | {1}".format(
                self.get_random(redirect_output=False, supports_output=True),
                command_string
            )
        else:
            return "{0} < {1}".format(command_string, random.choice(self.input_names))

    def _add_output_redirection(self, command_string: str) -> str:
        """Add random output redirection to the given command string."""
        if random.random() < self.pipe_probability:
            return "{0} | {1}".format(
                command_string,
                self.get_random(redirect_input=False, supports_input=True)
            )
        else:
            return random.choice(["{0} > {1}", "{0} >> {1}"]).format(
                command_string,
                random.choice(self.output_names)
            )
