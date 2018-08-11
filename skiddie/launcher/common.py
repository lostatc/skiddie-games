"""Common classes and functions for all game launcher interfaces.

Copyright © 2017 Wren Powell <wrenp@duck.com>

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
import enum
import time
import datetime
from typing import Callable

from skiddie.games import hash_cracker, shell_scripter, port_scanner, hex_editor
from skiddie.utils import get_description


class Difficulty(enum.Enum):
    """The difficulty level of a game."""
    EASY = "Easy"
    NORMAL = "Normal"
    HARD = "Hard"

    @classmethod
    def from_value(cls, value: str):
        """Get a Difficulty instance from its value.

        Args:
            value: The value of the difficulty to return. This is not case-sensitive.

        Returns:
            The first difficulty instance with the given value, or None if there is none.
        """
        for difficulty in cls:
            if difficulty.value.lower() == value.lower():
                return difficulty


# A function which launches a game with a given difficulty.
LauncherFunc = Callable[[Difficulty], None]

# A function which launches a game with a given difficulty and return the number of seconds it took to complete it.
TimerFunc = Callable[[Difficulty], float]


def _start_hash_cracker(difficulty: Difficulty) -> None:
    """Start the game "hash_cracker" with a given difficulty."""
    if difficulty is Difficulty.EASY:
        hash_cracker.play(rows_to_win=8, starting_rows=4, columns=6)
    if difficulty is Difficulty.NORMAL:
        hash_cracker.play(rows_to_win=8, starting_rows=4, columns=8)
    if difficulty is Difficulty.HARD:
        hash_cracker.play(rows_to_win=8, starting_rows=4, columns=10)


def _start_hex_editor(difficulty: Difficulty) -> None:
    """Start the game "hex_editor" with a given difficulty."""
    if difficulty is Difficulty.EASY:
        hex_editor.play(
            grids_to_win=1, grid_width=12, grid_height=6, forward_weight=2, sideways_weight=1,
            min_distance=1, max_distance=2,
        )
    if difficulty is Difficulty.NORMAL:
        hex_editor.play(
            grids_to_win=1, grid_width=16, grid_height=8, forward_weight=2, sideways_weight=2,
            min_distance=1, max_distance=2,
        )
    if difficulty is Difficulty.HARD:
        hex_editor.play(
            grids_to_win=1, grid_width=20, grid_height=10, forward_weight=2, sideways_weight=2,
            min_distance=1, max_distance=1,
        )


def _start_port_scanner(difficulty: Difficulty) -> None:
    """Start the game "port_scanner" with a given difficulty."""
    if difficulty is Difficulty.EASY:
        port_scanner.play(challenges_to_win=3, number_of_examples=1, max_section_number=63)
    if difficulty is Difficulty.NORMAL:
        port_scanner.play(challenges_to_win=3, number_of_examples=1, max_section_number=127)
    if difficulty is Difficulty.HARD:
        port_scanner.play(challenges_to_win=3, number_of_examples=1, max_section_number=255)


def _start_shell_scripter(difficulty: Difficulty) -> None:
    """Start the game "shell_scripter" with a given difficulty."""
    # With these settings, the average number of characters per command increases linearly with each difficulty level.
    if difficulty is Difficulty.EASY:
        shell_scripter.play(
            commands_to_win=15, min_args=0, max_args=3, redirect_probability=0.1, pipe_probability=0.2,
        )
    if difficulty is Difficulty.NORMAL:
        shell_scripter.play(
            commands_to_win=15, min_args=1, max_args=4, redirect_probability=0.3, pipe_probability=0.4,
        )
    if difficulty is Difficulty.HARD:
        shell_scripter.play(
            commands_to_win=15, min_args=2, max_args=5, redirect_probability=0.4, pipe_probability=0.5,
        )


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
        game_name: The name of the game.
        description: A description of the game.
        launcher: A function used to launch the game which returns the number of seconds taken to complete it.
    """
    def __init__(self, game_name: str, description: str, launcher: TimerFunc) -> None:
        self.game_name = game_name
        self.description = description
        self.launcher = launcher


class GameSession:
    """A session of a terminal game.

    Attributes:
        game: The game to be played.
        difficulty: The difficulty that the game is played on.
        username: The name of the user playing the game. None if no username has been set.
        duration: The number of seconds it took to complete the game. None if the game hasn't been played yet.
        completed: The time and date that the game was completed. None if hte game hasn't bee played yet.
    """
    def __init__(
            self, game: Game, difficulty: Difficulty,
            username: str = None, duration: float = None, completed: datetime.datetime = None):
        self.game = game
        self.difficulty = difficulty
        self.username = username
        self.duration = duration
        self.completed = completed

    @property
    def game_name(self):
        """A shortcut for accessing the name of the game."""
        return self.game.game_name

    @property
    def description(self):
        """A shortcut for accessing the description of the game."""
        return self.game.description

    def play(self):
        """Play the game with the current difficulty."""
        self.duration = self.game.launcher(self.difficulty)
        self.completed = datetime.datetime.now()


GAME_HASH_CRACKER = Game("hash_cracker", get_description("hash_cracker.md"), get_timer(_start_hash_cracker))
GAME_HEX_EDITOR = Game("hex_editor", get_description("hex_editor.md"), get_timer(_start_hex_editor))
GAME_PORT_SCANNER = Game("port_scanner", get_description("port_scanner.md"), get_timer(_start_port_scanner))
GAME_SHELL_SCRIPTER = Game("shell_scripter", get_description("shell_scripter.md"), get_timer(_start_shell_scripter))

# A list of all available games. This must be updated whenever new games are added.
GAMES = [GAME_HASH_CRACKER, GAME_HEX_EDITOR, GAME_PORT_SCANNER, GAME_SHELL_SCRIPTER]