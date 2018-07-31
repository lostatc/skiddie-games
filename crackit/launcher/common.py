import enum
import time
from typing import Callable

from crackit.games import hash_cracker, shell_scripter
from crackit.utils import get_description


class Difficulty(enum.Enum):
    """The difficulty level of a game."""
    EASY = 1
    NORMAL = 2
    HARD = 3


# A function which launches a game with a given difficulty.
LauncherFunc = Callable[[Difficulty], None]


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


class Game:
    def __init__(self, name: str, description: str, launcher: LauncherFunc) -> None:
        self.name = name
        self.description = description
        self.launcher = launcher


GAME_HASH_CRACKER = Game("hash_cracker", get_description("hash_cracker"), _start_hash_cracker)
GAME_SHELL_SCRIPTER = Game("shell_scripter", get_description("shell_scripter"), _start_shell_scripter)
