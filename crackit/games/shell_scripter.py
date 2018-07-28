"""A game about writing shell scripts.

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
import readline  # This is not unused. Importing it adds features to input().
from typing import List

from crackit.utils import clear_line, format_banner, LateInit

# The string that is printed before each command and line of user input.
COMMAND_PROMPT = "$ "

# All the characters that can be used to separate flags from their arguments.
FLAG_SEPARATORS = [" ", "="]

#
# The following constants are commonly used arguments for commands.
#

# Directory paths to be used as arguments in commands.
ARG_DIR_PATHS = [
    "~/Documents", "/home/lostatc/Documents", "~/Downloads", "/home/lostatc/Downloads", "~/Music",
    "/home/lostatc/Music", "~/Pictures", "/home/lostatc/Pictures", "~/Videos", "/home/lostatc/Videos", ".", "/", "/dev",
    "/dev/mapper", "/etc", "/etc/sysconfig", "/home/lostatc", "/mnt", "/proc", "/run", "/run/media/lostatc", "/sys",
    "/tmp", "/usr/share", "/usr/local/share", "/var", "/var/log",
]

# Shell globing patterns for matching file names to be used as arguments in commands.
ARG_FILE_GLOB_PATTERNS = [
    "\".*\"", "\"*.png\"", "\"*.flac\"", "\"*.log\"", "\"*.pid\"", "\"*.rst\"", "\"*.tar.*\"", "\"*.py[cod]\"",
    "\"*.od[tspgf]\"", "*.og[gvaxm]", "\"*.doc[xm]\"", "\"*.xls[xm]\"", "\"backup.tar-[a-z][a-z]\"",
]

# Delimiters to be used as arguments in commands.
ARG_DELIMITERS = [
    "\" \"", "\",\"", "\"-\"", "\"_\"", "\"|\"", "\":\"", "\"\\n\"", "\"\\0\"",
]

# The list of possible names of files that can be used for data input.
ARG_INPUT_FILE_NAMES = [
    "input.txt", "input_file.txt", "in.txt", "origin.txt", "source.txt", "src.txt", "data.txt", "beginning.txt",
    "start.txt", "info.txt",
]

# The list of possible names of files that can be used for data output.
ARG_OUTPUT_FILE_NAMES = [
    "output.txt", "output_file.txt", "out.txt", "result.txt", "destination.txt", "dest.txt", "file.txt", "end.txt",
    "finish.txt", "dump.txt",
]


class Argument:
    """An argument to a shell command.

    Attributes:
        names: A list of possible names for the argument.
        values: A list of possible values for the argument.
    """
    def __init__(self, names: List[str], values: List[str]) -> None:
        self.names = names
        self.values = values

    def get_random(self, separator: str) -> str:
        """Generate a random argument within the given constraints as a string.

        Args:
            separator: The string used to separate the argument from its value.

        Returns:
            The argument as a string.
        """
        # Don't print the separator if either the list of names or list of values are empty.
        return separator.join(random.choice(choices) for choices in (self.names, self.values) if choices)


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
        min_args: The minimum number of non-required arguments that a command can have.
        max_args: The maximum number of non-required arguments that a command can have.
        redirect_probability: The probability that a command will send its output to a pipe or file.
        pipe_probability: The probability that a command will use a pipe when redirecting its output.
    """
    min_args = LateInit()
    max_args = LateInit()
    redirect_probability = LateInit()
    pipe_probability = LateInit()

    def __init__(
            self, name: str, positional_args: List[Argument], optional_args: List[Argument],
            redirect_output: bool = False, redirect_input: bool = False) -> None:
        self.name = name
        self.positional_args = positional_args
        self.optional_args = optional_args
        self.redirect_output = redirect_output
        self.redirect_input = redirect_input

    def get_random(self, redirect_input: bool = True, redirect_output: bool = True) -> str:
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
            command_string = self.name
        else:
            command_string = "{0} {1}".format(self.name, " ".join(arg.get_random(flag_separator) for arg in selected_args))

        # Add random redirects to the command string.
        if self.redirect_input and redirect_input:
            command_string = self._add_input_redirection(command_string)
        if self.redirect_output and redirect_output and random.random() < self.redirect_probability:
            command_string = self._add_output_redirection(command_string)

        return command_string

    def _add_input_redirection(self, command: str) -> str:
        """Add random input redirection to the given command string."""
        def create_file_redirect() -> str:
            return "{0} < {1}".format(command, random.choice(ARG_INPUT_FILE_NAMES))

        def create_pipe_redirect() -> str:
            try:
                input_command = random.choice([item for item in COMMANDS if item.redirect_output and item != self])
            except IndexError:
                return command

            return "{0} | {1}".format(input_command.get_random(redirect_output=False), command)

        if random.random() < self.pipe_probability:
            return create_pipe_redirect()
        else:
            return create_file_redirect()

    def _add_output_redirection(self, command: str) -> str:
        """Add random output redirection to the given command string."""
        def create_file_redirect() -> str:
            return "{0} > {1}".format(command, random.choice(ARG_OUTPUT_FILE_NAMES))

        def create_pipe_redirect() -> str:
            try:
                output_command = random.choice([item for item in COMMANDS if item.redirect_input and item != self])
            except IndexError:
                return command

            return "{0} | {1}".format(command, output_command.get_random(redirect_input=False))

        if random.random() < self.pipe_probability:
            return create_pipe_redirect()
        else:
            return create_file_redirect()


COMMANDS = (
    Command(
        "grep", [
            Argument(
                ["-e", "--regexp"], [
                    "\"^[0-9]+$\"", "\"[KMGT](B|iB)\"", "\"[a-f0-9]{6}\"", "\"^https?://\"", "\"[04567]{3}\"",
                    "\"^/\w*(:/\w*)*$\"", "\"([r-][w-][x-]){3}\"", "^[\w=]+(,[\w=]+)*$", "Error", "Exception",
                    "Warning", "Info", "NULL", "true", "false",
                ],
            ),
        ], [
            Argument(["-E", "--extended-regexp", "-G", "--basic-regexp", "-F", "--fixed-string"], []),
            Argument(["-i", "--ignore-case"], []),
            Argument(["-v", "--invert-match"], []),
            Argument(["-x", "--line-regexp"], []),
            Argument(["-c", "--count"], []),
            Argument(["--color"], ["never", "always", "auto"]),
            Argument(["-m", "--max-count"], ["1", "2", "3", "4", "5"]),
            Argument(["-A", "--after-context"], ["1", "2", "3", "4", "5", "10"]),
            Argument(["-B", "--before-context"], ["1", "2", "3", "4", "5", "10"]),
            Argument(["--exclude"], ARG_FILE_GLOB_PATTERNS),
            Argument(["--include"], ARG_FILE_GLOB_PATTERNS),
            Argument(["-r", "--recursive"], []),
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
            Argument(["-amin"], ["1", "2", "3", "4", "5", "10", "15", "20", "25", "30", "60", "120"]),
            Argument(["-cmin"], ["1", "2", "3", "4", "5", "10", "15", "20", "25", "30", "60", "120"]),
            Argument(["-empty"], []),
            Argument(["-gid"], ["0", "10", "100", "99", "1000", "1001", "1002", "1003"]),
            Argument(["-group"], ["root", "lostatc", "wheel", "nobody", "users"]),
            Argument(["-links"], ["0", "1", "2", "3", "4", "5"]),
            Argument(["-mmin"], ["1", "2", "3", "4", "5", "10", "15", "20", "25", "30", "60", "120"]),
            Argument(["-name"], ARG_FILE_GLOB_PATTERNS),
            Argument(["-perm"], ["\"/a+w\"", "\"-g+w\"", "\"u=w\"", "\"-a+r\"", "\"/a+x\"", "\"-220\""]),
            Argument(["-size"], ["50K", "100K", "120K", "1M", "50M", "100M", "200M", "1G", "2G", "3G"]),
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
            Argument(
                ["-b", "--bytes"],
                ["\"-4\"", "\"-8\"", "\"-16\"", "\"1-\"", "\"2-\"", "\"4-\"", "\"1-2\"", "\"2-4\"", "\"4-8\""]
            ),
            Argument(
                ["-c", "--characters"],
                ["1", "\"-10\"", "\"-3\"", "\"-5\"", "\"1-5\"", "\"1-2\"", "\"5-\"", "\"-20\""]
            ),
            Argument(
                ["-f", "--fields"],
                ["1", "2", "3", "4", "5", "\"1-\"", "\"2-\"", "\"-3\"", "\"-5\"", "\"1-2\"", "\"2-3\""]
            ),
            Argument(["-d", "--delimiter"], ARG_DELIMITERS),
            Argument(["--complement"], []),
            Argument(["-s", "--only-delimited"], []),
            Argument(["--output-delimiter"], ARG_DELIMITERS),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "sort", [], [
            Argument(["-d", "--dictionary-order"], []),
            Argument(["-f", "--ignore-case"], []),
            Argument(["-i", "--ignore-nonprinting"], []),
            Argument(["-n", "--numeric-sort"], []),
            Argument(["-r", "--reverse"], []),
            Argument(["--sort"], ["general-numeric", "human-numeric", "month", "numeric", "random", "version"]),
            Argument(["-s", "--stable"], []),
            Argument(["-t", "--field-separator"], ARG_DELIMITERS),
            Argument(["--parallel"], ["1", "2", "3", "4", "5", "6"]),
            Argument(["-k", "--key"], ["1", "2", "3", "1,2", "1,3" "2,3", "1.2", "2.3", "1.2,4", "2.2,3.2"]),

        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "head", [], [
            Argument(["-c", "--bytes"], ["64", "128", "256", "512", "1K", "2K", "3K", "4K", "1M"]),
            Argument(["-n", "--lines"], ["1", "2", "3", "4", "5", "15", "\"-15\"", "20", "\"-20\"", "25", "\"-25\""]),
            Argument(["-q", "--quiet", "--silent"], []),
            Argument(["-z", "--zero-terminated"], []),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "tail", [], [
            Argument(["-c", "--bytes"], ["64", "128", "256", "512", "1K", "2K", "3K", "4K", "1M"]),
            Argument(["-f", "--follow"], ["name", "descriptor"]),
            Argument(["-n", "--lines"], ["1", "2", "3", "4", "5", "15", "\"-15\"", "20", "\"-20\"", "25", "\"-25\""]),
            Argument(["--pid"], ["451", "1984", "24601", "666", "6022", "3141", "2718", "1414", "1618"]),
            Argument(["-q", "--quiet", "--silent"], []),
            Argument(["--retry"], []),
            Argument(["-s", "--sleep-interval"], ["0.1", "0.25", "0.5", "2", "3", "5", "10"]),
            Argument(["-z", "--zero-terminated"], []),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "cat", [
            Argument([], ARG_INPUT_FILE_NAMES),
        ], [
            Argument(["-A", "--show-all"], []),
            Argument(["-e"], []),
            Argument(["-E", "--show-ends"], []),
            Argument(["-n", "--number"], []),
            Argument(["-s", "--squeeze-blank"], []),
            Argument(["-t"], []),
            Argument(["-T", "--show-tabs"], []),
            Argument(["-v", "--show-nonprinting"], []),
        ],
        redirect_output=True,
    ),
    Command(
        "diff", [
            Argument([], ARG_INPUT_FILE_NAMES),
            Argument([], ARG_INPUT_FILE_NAMES),
        ], [
            Argument(["-q", "--brief"], []),
            Argument(["-s", "--report-identical-files"], []),
            Argument(["-c", "-C", "--context"], ["0", "1", "2", "4", "5", "6", "7", "8", "9", "10"]),
            Argument(["-u", "-U", "--unified"], ["0", "1", "2", "4", "5", "6", "7", "8", "9", "10"]),
            Argument(["-y", "--side-by-side"], []),
            Argument(["-W", "--width"], ["64", "72", "80", "100", "120", "200"]),
            Argument(["--tabsize"], ["1", "2", "4"]),
            Argument(["-r", "--recursive"], []),
            Argument(["--no-dereference"], []),
            Argument(["-x", "--exclude"], ARG_FILE_GLOB_PATTERNS),
            Argument(["-i", "--ignore-case"], []),
            Argument(["-a", "--text"], []),
            Argument(["--color"], ["never", "always", "auto"]),
        ],
        redirect_output=True,
    ),
    Command(
        "tee", [
            Argument([], ARG_OUTPUT_FILE_NAMES),
        ], [
            Argument(["-a", "--append"], []),
            Argument(["-i", "--ignore-interrupts"], []),
            Argument(["-p"], []),
            Argument(["--output-error"], ["warn", "warn-nopipe", "exit", "exit-nopipe"]),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "paste", [], [
            Argument(["-d", "--delimiters"], ARG_DELIMITERS),
            Argument(["-s", "--serial"], []),
            Argument(["-z", "--zero-terminated"], []),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "shuf", [], [
            Argument(["-n", "--head-count"], ["5", "10", "15", "20", "25", "30"]),
            Argument(["--random-source"], ["/dev/random", "/dev/urandom", "<(echo \"4\")"]),
            Argument(["-r", "--repeat"], []),
            Argument(["-z", "--zero-terminated"], []),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "mv", [
            Argument([], ARG_INPUT_FILE_NAMES),
            Argument([], ARG_OUTPUT_FILE_NAMES),
        ], [
            Argument(["--backup"], ["none", "off", "numbered", "exiting", "nil", "simple", "never"]),
            Argument(["-f", "--force"], []),
            Argument(["-i", "--interactive"], []),
            Argument(["-n", "--no-clobber"], []),
            Argument(["--strip-trailing-slashes"], []),
            Argument(["-S", "--suffix"], ["\".bak\"", "\".backup\"", "\".old\"", "\".orig\""]),
            Argument(["-u", "--update"], []),
        ],
    ),
    Command(
        "cp", [
            Argument([], ARG_INPUT_FILE_NAMES),
            Argument([], ARG_OUTPUT_FILE_NAMES),
        ], [
            Argument(["-a", "--archive"], []),
            Argument(["--backup"], ["none", "off", "numbered", "exiting", "nil", "simple", "never"]),
            Argument(["-f", "--force"], []),
            Argument(["-i", "--interactive"], []),
            Argument(["-L", "--dereference"], []),
            Argument(["-n", "--no-clobber"], []),
            Argument(["-P", "--no-dereference"], []),
            Argument(["--preserve"], ["mode", "ownership", "timestamps", "context", "links", "xattr", "all"]),
            Argument(["--no-preserve"], ["mode", "ownership", "timestamps", "context", "links", "xattr", "all"]),
            Argument(["-r", "-R", "--recursive"], []),
            Argument(["--reflink"], ["always", "auto"]),
            Argument(["--sparse"], ["always", "auto", "never"]),
            Argument(["-s", "--symbolic-link"], []),
            Argument(["-S", "--suffix"], ["\".bak\"", "\".backup\"", "\".old\"", "\".orig\""]),
            Argument(["-u", "--update"], []),
            Argument(["-x", "--one-file-system"], []),
        ],
    ),
    Command(
        "rm", [
            Argument([], ARG_INPUT_FILE_NAMES),
        ], [
            Argument(["-f", "--force"], []),
            Argument(["--interactive"], ["never", "once", "always"]),
            Argument(["--one-file-system"], []),
            Argument(["--no-preserve-root"], []),
            Argument(["-r", "-R", "--recursive"], []),
            Argument(["-d", "--dir"], []),
        ]
    ),
)


def main(
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

    # Print random commands and prompt the user to type them in until they type them in correctly.
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
