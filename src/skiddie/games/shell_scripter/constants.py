"""Constants used to generate commands.

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
from skiddie.games.shell_scripter.logic import Command, Argument

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
INPUT_FILE_NAMES = [
    "input.txt", "input_file.txt", "in.txt", "origin.txt", "source.txt", "src.txt", "data.txt", "beginning.txt",
    "start.txt", "info.txt",
]

# The list of possible names of files that can be used for data output.
OUTPUT_FILE_NAMES = [
    "output.txt", "output_file.txt", "out.txt", "result.txt", "destination.txt", "dest.txt", "file.txt", "end.txt",
    "finish.txt", "dump.txt",
]

COMMANDS = (
    Command(
        "grep", [
            Argument(
                ["-e", "--regexp"], [
                    "\"^[0-9]+$\"", "\"[KMGT](B|iB)\"", "\"[a-f0-9]{6}\"", "\"^https?://\"", "\"[04567]{3}\"",
                    "\"^/\w*(:/\w*)*$\"", "\"([r-][w-][x-]){3}\"", "^[\w-=]+(,[\w-=]+)*$", "Error", "Exception",
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
            Argument([], INPUT_FILE_NAMES),
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
            Argument([], INPUT_FILE_NAMES),
            Argument([], INPUT_FILE_NAMES),
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
            Argument([], OUTPUT_FILE_NAMES),
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
        "uniq", [], [
            Argument(["-c", "--count"], []),
            Argument(["-d", "--repeated"], []),
            Argument(["--all-repeated"], ["none", "prepend", "separate"]),
            Argument(["-f", "--skip-fields"], ["1", "2", "3", "4", "5"]),
            Argument(["--group"], ["separate", "prepend", "append", "both"]),
            Argument(["-i", "--ignore-case"], []),
            Argument(["-s", "--skip-chars"], ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]),
            Argument(["-u", "--unique"], []),
            Argument(["-z", "--zero-terminated"], []),
            Argument(["-w", "--check-chars"], ["1", "5", "10", "15", "20", "25", "30", "40", "50"]),
        ],
        redirect_input=True,
        redirect_output=True,
    ),
    Command(
        "mv", [
            Argument([], INPUT_FILE_NAMES),
            Argument([], OUTPUT_FILE_NAMES),
        ], [
            Argument(["--backup"], ["none", "off", "numbered", "existing", "nil", "simple", "never"]),
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
            Argument([], INPUT_FILE_NAMES),
            Argument([], OUTPUT_FILE_NAMES),
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
            Argument([], INPUT_FILE_NAMES),
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
