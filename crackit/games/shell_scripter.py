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

The objective of this game is to type out the given randomly generated Linux shell commands as quickly and accurately as
possible. If a command is typed incorrectly, it is cleared.
"""
import random
import readline  # This is not unused. Importing it adds features to input().
from typing import List

from crackit.utils import clear_line, format_banner

# The string that is printed before each command and line of user input.
COMMAND_PROMPT = "$ "

# All the characters that can be used to separate flags from their arguments.
FLAG_SEPARATORS = [" ", "="]

# The minimum number of non-required arguments that a command can have.
MIN_ARGS = 0

# The maximum number of non-required arguments that a command can have.
MAX_ARGS = 5

# The probability that a command will send its output to a pipe or file.
OUTPUT_REDIRECTION_PROBABILITY = 0.25

# The list of possible names of files that the output of a command can be redirected to.
OUTPUT_FILE_NAMES = [
    "output.txt", "output", "output_file.txt", "output_file", "results.txt", "results", "file.txt",
    "file",
]

# The list of possible names of files that the input of a command can be redirected from.
INPUT_FILE_NAMES = [
    "input.txt", "input", "input_file.txt", "input_file", "source.txt", "source", "data.txt", "data",
]

#
# The following constants are commonly used arguments for commands.
#

# Directory paths to be used as arguments in commands.
ARG_DIR_PATHS = [
    "~/Documents", "/home/lostatc/Documents", "~/Downloads", "/home/lostatc/Downloads", "~/Music",
    "/home/lostatc/Music", "~/Pictures", "/home/lostatc/Pictures", "~/Videos", "/home/lostatc/Vidoes", ".", "/", "/dev",
    "/etc", "/home/lostatc", "/mnt", "/proc", "/run", "/run/media/lostatc", "/sys", "/tmp", "/usr/share",
    "/usr/local/share", "/var", "/var/log",
]

# Shell globing patterns for matching file names to be used as arguments in commands.
ARG_FILE_GLOB_PATTERNS = [
    "\"*.png\"", "\"*.jpg\"", "\"*.mp3\"", "\"*.flac\"", "\"*.mp4\"", "\"*.log\"", "\"*.tar.*\"",
    "\"*.od[tspgf]\"", "\".*\"", "\"*.doc[xm]\"", "\"*.xls[xm]\"",
]

# Number ranges to be used as arguments in the `cut` command.
ARG_CUT_RANGES = [
    "1", "\"-10\"", "\"3-\"", "\"2-4\"", "\"1-2\"", "\"5-\"", "\"-20\"",
]

# Delimiters to be used as arguments in the `cut` command.
ARG_CUT_DELIMITERS = [
    "\" \"", "\",\"", "\"|\"", "\"\\n\"", "\"\\0\"",
]


class Argument:
    """An argument for a shell command that the user can be prompted to type.

    Attributes:
        names: All the names that the command can have.
        args: A list of possible arguments for the command.
    """
    def __init__(self, names: List[str], args: List[str]) -> None:
        self.names = names
        self.args = args

    def get_random(self, flag_separator: str) -> str:
        """Generate a random argument within the given constraints as a string.

        Args:
            flag_separator: The string used to separate flags from their arguments.

        Returns:
            The argument as a string.
        """
        return flag_separator.join(random.choice(choices) for choices in (self.names, self.args) if choices)


# TODO: Accept multiple lists for possible_args to account for mutually-exclusive arguments.
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

    def get_random(self, redirect_input=True, redirect_output=True) -> str:
        """Generate a random command string within the given constraints.

        Args:
            redirect_input: Have a chance of adding random input redirection to the command string.
            redirect_output: Have a chance of adding random output redirection to the command string.

        Returns:
            The command as a string.
        """
        selected_args = self.positional_args.copy()
        remaining_args = self.optional_args.copy()

        # Select random parameters.
        flag_separator = random.choice(FLAG_SEPARATORS)
        number_of_args = random.randrange(MIN_ARGS, MAX_ARGS)

        # Add a random number of optional arguments.
        random.shuffle(remaining_args)
        for _ in range(number_of_args):
            try:
                selected_args.append(remaining_args.pop())
            except IndexError:
                break

        # Generate a command string.
        if not selected_args:
            command_string = self.name
        else:
            command_string = "{0} {1}".format(self.name, " ".join(arg.get_random(flag_separator) for arg in selected_args))

        # Add random redirects to the command string.
        if self.redirect_input and redirect_input:
            command_string = self._add_input_redirection(command_string)
        if self.redirect_output and redirect_output and random.random() < OUTPUT_REDIRECTION_PROBABILITY:
            command_string = self._add_output_redirection(command_string)

        return command_string

    def _add_input_redirection(self, command: str) -> str:
        """Add random input redirection to the given command string."""
        def create_file_redirect():
            return "{0} < {1}".format(command, random.choice(INPUT_FILE_NAMES))

        def create_pipe_redirect():
            try:
                input_command = random.choice([item for item in COMMANDS if item.redirect_output and item != self])
            except IndexError:
                return command

            return "{0} | {1}".format(input_command.get_random(redirect_output=False), command)

        return random.choice([
            create_file_redirect(),
            create_pipe_redirect(),
        ])

    def _add_output_redirection(self, command: str) -> str:
        """Add random output redirection to the given command string."""
        def create_file_redirect():
            return "{0} > {1}".format(command, random.choice(OUTPUT_FILE_NAMES))

        def create_pipe_redirect():
            try:
                output_command = random.choice([item for item in COMMANDS if item.redirect_input and item != self])
            except IndexError:
                return command

            return "{0} | {1}".format(command, output_command.get_random(redirect_input=False))

        return random.choice([
            create_file_redirect(),
            create_pipe_redirect(),
        ])


COMMANDS = (
    Command(
        "grep", [
            Argument(
                ["-e", "--regexp"], [
                    "\"^[0-9]+$\"", "\"[KMGT](B|iB)\"", "\"[a-f0-9]{6}\"", "\"^https?://\"", "\"[04567]{3}\"",
                    "\"^/\w(:/\w)*$\"", "\"([r-][w-][x-]){3}\"", "Error", "Exception", "Warning", "Info", "NULL",
                    "true", "false",
                ],
            ),
        ], [
            Argument(["-E", "--extended-regexp", "-G", "--basic-regexp", "-F", "--fixed-string"], []),
            Argument(["-i", "--ignore-case"], []),
            Argument(["-v", "--invert-match"], []),
            Argument(["-x", "--line-regexp"], []),
            Argument(["-c", "--count"], []),
            Argument(["-m", "--max-count"], ["1", "2", "3", "4", "5"]),
            Argument(["-A", "--after-context", "-B", "--before-context"], ["1", "2", "5", "10"]),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "find", [
            Argument([], ARG_DIR_PATHS),
        ], [
            Argument(["-depth"], []),
            Argument(["-maxdepth"], ["0", "1", "2", "3", "4", "5"]),
            Argument(["-mindepth"], ["0", "1", "2", "3", "4", "5"]),
            Argument(["-mount"], []),
            Argument(["-amin"], ["1", "5", "10", "15", "20", "25", "30"]),
            Argument(["-cmin"], ["1", "5", "10", "15", "20", "25", "30"]),
            Argument(["-empty"], []),
            Argument(["-gid"], ["0", "10", "100", "99", "1000", "1001", "1002", "1003"]),
            Argument(["-group"], ["root", "lostatc", "wheel", "nobody", "users"]),
            Argument(["-links"], ["0", "1", "2", "3", "4", "5"]),
            Argument(["-mmin"], ["1", "5", "10", "15", "20", "25", "30"]),
            Argument(["-name"], ARG_FILE_GLOB_PATTERNS),
            Argument(["-perm"], ["\"/a+w\"", "\"-g+w\"", "\"u=w\"", "\"-a+r\"", "\"/a+x\"", "\"-220\""]),
            Argument(["-size"], ["100k", "120K", "50M", "200M", "1G", "10G"]),
            Argument(["-delete"], []),
            Argument(["-print"], []),
            Argument(["-ls"], []),
            Argument(["-prune"], []),
        ],
        redirect_output=True,
    ),
    Command(
        "ls", [
            Argument([], ARG_DIR_PATHS),
        ], [
            Argument(["-a", "--all"], []),
            Argument(["-d", "--directory"], []),
            Argument(["--hide"], ARG_FILE_GLOB_PATTERNS),
            Argument(["-l"], []),
            Argument(["-N", "--literal"], []),
            Argument(["-Q", "--quote-name"], []),
            Argument(["-r", "--reverse"], []),
            Argument(["-s", "--size"], []),
            Argument(["-R", "--recursive"], []),
            Argument(["--quoting-style"], ["literal", "locale", "shell", "shell-always", "shell-escape", "shell-escape-always", "c", "escape"]),
            Argument(["--color"], ["always", "auto", "never"]),
            Argument(["--format"], ["across", "commas", "horizontal", "long", "single-column", "verbose", "vertical"]),
        ],
        redirect_output=True,
    ),
    Command(
        "cut", [], [
            Argument(["-b", "--bytes"], ARG_CUT_RANGES),
            Argument(["-c", "--characters"], ARG_CUT_RANGES),
            Argument(["-d", "--delimiter"], ARG_CUT_DELIMITERS),
            Argument(["-f", "--fields"], ARG_CUT_RANGES),
            Argument(["--complement"], []),
            Argument(["-s", "--only-delimited"], []),
            Argument(["--output-delimiter"], ARG_CUT_DELIMITERS),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
)


def main(commands_to_win: int = 10) -> None:
    """Play the game.

    Args:
        commands_to_win: The number of commands that must be correctly entered to win the game.
    """
    for _ in range(commands_to_win):
        command_string = random.choice(COMMANDS).get_random()
        print(COMMAND_PROMPT + command_string)

        while True:
            if input(COMMAND_PROMPT) == command_string:
                break
            else:
                clear_line()

        print()

    print(format_banner("ACCESS GRANTED", ansi="\x1b[1;32m"))


if __name__ == "__main__":
    main()
