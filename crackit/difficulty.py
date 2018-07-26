import enum

from crackit.games import hash_cracker, shell_scripter


class Difficulty(enum.Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3


def start_hash_cracker(difficulty: Difficulty) -> None:
    """Start the game "hash_cracker" with a given difficulty."""
    if difficulty is Difficulty.EASY:
        hash_cracker.main(rows_to_win=8, starting_rows=4, columns=6)
    if difficulty is Difficulty.NORMAL:
        hash_cracker.main(rows_to_win=8, starting_rows=4, columns=8)
    if difficulty is Difficulty.HARD:
        hash_cracker.main(rows_to_win=8, starting_rows=4, columns=10)


def start_shell_scripter(difficulty: Difficulty) -> None:
    """Start the game "shell_scripter" with a given difficulty."""
    # With these settings, the average number of characters per command increases linearly with each difficulty level.
    if difficulty is Difficulty.EASY:
        shell_scripter.main(commands_to_win=15, min_args=0, max_args=3, redirect_probability=0.1, pipe_probability=0.2)
    if difficulty is Difficulty.NORMAL:
        shell_scripter.main(commands_to_win=15, min_args=1, max_args=4, redirect_probability=0.3, pipe_probability=0.4)
    if difficulty is Difficulty.HARD:
        shell_scripter.main(commands_to_win=15, min_args=2, max_args=5, redirect_probability=0.4, pipe_probability=0.5)
