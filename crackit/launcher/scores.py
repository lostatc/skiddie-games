"""The leaderboard for tracking player scores.

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
import os
import json
import getpass
from typing import List, Optional

from prompt_toolkit import prompt

from crackit.constants import SCORES_FILE, GUI_STYLE, CONFIG_DIR
from crackit.utils import format_duration, LateInit, bool_prompt
from crackit.launcher.common import GameSession, Game, Difficulty

# The string that immediately precedes the users time whenever their time is printed to stdout.
TIMER_RESULT_PREFIX = "Your time is: "

# The number of spaces to indent when serializing JSON.
JSON_INDENT = 4

# The message to display when the user sets a new high score.
NEW_HIGH_SCORE_MESSAGE = "You've set a new high score!"


class ScoreStore:
    """Persistent storage of the user's scores.

    Attributes:
        _path: The path of the JSON file.
        _data: The data contained in the JSON file.
    """
    def __init__(self) -> None:
        self._path = SCORES_FILE
        self._data = LateInit("cannot access data before the `read` method is called")

    def read(self) -> None:
        """Read the scores from storage."""
        try:
            with open(self._path, "r") as file:
                self._data = json.load(file)
        except FileNotFoundError:
            # The file has not been created yet.
            self._data = {}

    def write(self) -> None:
        """Write the scores to storage."""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(self._path, "w") as file:
            json.dump(self._data, file, indent=JSON_INDENT)

    def add_score(self, session: GameSession) -> None:
        """Add a score.

        Args:
            session: The session of the game where the score was set.
        """
        new_score = {"username": session.username, "duration": session.duration}
        (self._data
            .setdefault(session.game_name, {})
            .setdefault(session.difficulty.value, [])
            .append(new_score))

    def get_scores(self, game: Game, difficulty: Difficulty, sort=True) -> List[GameSession]:
        """Return a list of scores from the given game on the given difficulty.

        Returns:
            A list of sessions of games.
        """
        try:
            scores = [
                GameSession(game, difficulty, username=score["username"], duration=score["duration"])
                for score in self._data[game.game_name][difficulty.value]
            ]

            if sort:
                scores.sort(key=lambda x: x.duration)

            return scores
        except KeyError:
            # There are no scores for the given game and difficulty.
            return []

    def get_high_score(self, game: Game, difficulty: Difficulty) -> Optional[GameSession]:
        """Get the score with the best time for the given game and difficulty.

        Returns:
            The session for the game with the high score or None if there are no scores.
        """
        try:
            max(self.get_scores(game, difficulty), key=lambda x: x.duration)
        except ValueError:
            # There are no scores for the given game and difficulty.
            return None


def process_result(session: GameSession) -> None:
    """Process the duration that the user played a game for.

    Args:
        session: The session of the game to process the result of.

    Raises:
        ValueError: A GameSession was passed in which had not been played yet.
    """
    if session.duration is None:
        raise ValueError("the game has not been played yet")

    # Get all the user's past scores.
    score_store = ScoreStore()
    score_store.read()

    # Inform the user if they've set a new high score.
    high_score = score_store.get_high_score(session.game, session.difficulty)
    if high_score is None or high_score.duration < session.duration:
        print(NEW_HIGH_SCORE_MESSAGE)

    # Print score to stdout.
    print(TIMER_RESULT_PREFIX + format_duration(session.duration))

    # Ask user if they want to save their score.
    save_score = bool_prompt("Would you like to save your score? [Y/n]: ", default=True)

    if not save_score:
        return

    # Prompt user for username.
    username = prompt(message="Name for the new score: ", default=getpass.getuser())
    session.username = username

    # Record score.
    score_store.add_score(session)
    score_store.write()
