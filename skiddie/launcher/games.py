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
import datetime
from typing import Callable

from skiddie.games import hash_cracker, shell_scripter, port_scanner, hex_editor, pattern_finder, database_querier
from skiddie.launcher.difficulty import DifficultyPresets
from skiddie.utils.misc import get_timer
from skiddie.utils.ui import get_description


class Game:
    """A terminal game.

    Attributes:
        game_name: The name of the game.
        description: A description of the game.
        launcher: A function which starts the game.
    """
    def __init__(self, game_name: str, description: str, launcher: Callable[..., None]) -> None:
        self.game_name = game_name
        self.description = description
        self._launcher = launcher

    def play(self, difficulty: str) -> float:
        """Play the game and return how long it took to complete in seconds.

        Args:
            difficulty: The difficulty to play the game on.
        """
        difficulty_store = DifficultyPresets()
        difficulty_store.read()
        game_args = difficulty_store.get_difficulty_settings(self.game_name, difficulty)
        difficulty_store.write()

        play_func = get_timer(self._launcher)

        return play_func(**game_args)


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
            self, game: Game, difficulty: str, username: str = None, duration: float = None,
            completed: datetime.datetime = None):
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
        self.duration = self.game.play(self.difficulty)
        self.completed = datetime.datetime.now()


GAME_DATABASE_QUERIER = Game("database_querier", get_description("database_querier.md"), database_querier.play)
GAME_HASH_CRACKER = Game("hash_cracker", get_description("hash_cracker.md"), hash_cracker.play)
GAME_HEX_EDITOR = Game("hex_editor", get_description("hex_editor.md"), hex_editor.play)
GAME_PATTERN_FINDER = Game("pattern_finder", get_description("pattern_finder.md"), pattern_finder.play)
GAME_PORT_SCANNER = Game("port_scanner", get_description("port_scanner.md"), port_scanner.play)
GAME_SHELL_SCRIPTER = Game("shell_scripter", get_description("shell_scripter.md"), shell_scripter.play)

# A list of all available games. This must be updated whenever new games are added.
GAMES = [
    GAME_DATABASE_QUERIER, GAME_HASH_CRACKER, GAME_HEX_EDITOR, GAME_PATTERN_FINDER, GAME_PORT_SCANNER,
    GAME_SHELL_SCRIPTER
]
