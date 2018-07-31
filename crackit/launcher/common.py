"""Common classes and functions for all game launcher interfaces.

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
import enum
import time
from typing import Callable

from crackit.games import hash_cracker, shell_scripter
from crackit.utils import get_description, format_duration


class Difficulty(enum.Enum):
    """The difficulty level of a game."""
    EASY = 1
    NORMAL = 2
    HARD = 3


# A function which launches a game with a given difficulty.
LauncherFunc = Callable[[Difficulty], None]

# A function which launches a game with a given difficulty and return the number of seconds it took to complete it.
TimerFunc = Callable[[Difficulty], float]


def _start_hash_cracker(difficulty: Difficulty) -> None:
    """Start the game "hash_cracker" with a given difficulty."""
    if difficulty is Difficulty.EASY:
        hash_cracker.main(rows_to_win=8, starting_rows=4, columns=6)
    if difficulty is Difficulty.NORMAL:
        hash_cracker.main(rows_to_win=8, starting_rows=4, columns=8)
    if difficulty is Difficulty.HARD:
        hash_cracker.main(rows_to_win=8, starting_rows=4, columns=10)


def _start_shell_scripter(difficulty: Difficulty) -> None:
    """Start the game "shell_scripter" with a given difficulty."""
    # With these settings, the average number of characters per command increases linearly with each difficulty level.
    if difficulty is Difficulty.EASY:
        shell_scripter.main(commands_to_win=15, min_args=0, max_args=3, redirect_probability=0.1, pipe_probability=0.2)
    if difficulty is Difficulty.NORMAL:
        shell_scripter.main(commands_to_win=15, min_args=1, max_args=4, redirect_probability=0.3, pipe_probability=0.4)
    if difficulty is Difficulty.HARD:
        shell_scripter.main(commands_to_win=15, min_args=2, max_args=5, redirect_probability=0.4, pipe_probability=0.5)


def get_timer(launcher_func: LauncherFunc) -> TimerFunc:
    """Get a function which times how long it takes to finish a game.

    Args:
        launcher_func: A function that executes a game.

    Returns:
        A function which returns the number of seconds that the game took to execute.
    """
    def timer(difficulty: Difficulty) -> float:
        start_time = time.monotonic()
        launcher_func(difficulty)
        end_time = time.monotonic()

        elapsed_time = end_time - start_time

        return elapsed_time

    return timer


class Game:
    """A terminal game.

    Attributes:
        name: The name of the game.
        description: A description of the game.
        launcher: A function used to launch the game which returns the number of seconds taken to complete it.
    """
    def __init__(self, name: str, description: str, launcher: TimerFunc) -> None:
        self.name = name
        self.description = description
        self.launcher = launcher


GAME_HASH_CRACKER = Game("hash_cracker", get_description("hash_cracker"), get_timer(_start_hash_cracker))
GAME_SHELL_SCRIPTER = Game("shell_scripter", get_description("shell_scripter"), get_timer(_start_shell_scripter))

# A list of all available games.
GAMES = [GAME_HASH_CRACKER, GAME_SHELL_SCRIPTER]
