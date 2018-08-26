"""The leaderboard for tracking player scores.

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
import os
import json
import getpass
import datetime
from typing import List, Optional, Union, Callable, Any

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from skiddie.exceptions import MissingConfigKeyError

from skiddie.constants import SCORES_FILE, CONFIG_DIR, JSON_INDENT
from skiddie.utils.ui import format_duration, bool_prompt, format_table
from skiddie.utils.misc import LateInit, get_first_insensitive_key
from skiddie.launcher.games import GameSession, Game

# The string that immediately precedes the users time whenever their time is printed to stdout.
TIMER_RESULT_PREFIX = "Your time is: "

# The message to display when the user sets a new high score.
NEW_HIGH_SCORE_MESSAGE = "You've set a new high score!"


class Scores:
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
            json.dump(self._data, file, indent=JSON_INDENT, sort_keys=True)

    def add_score(self, session: GameSession) -> None:
        """Add a score.

        Args:
            session: The session of the game where the score was set.
        """
        new_score = {
            "username": session.username,
            "duration": session.duration,
            "completed": session.completed.timestamp()
        }

        (self._data
            .setdefault(session.game_name, {})
            .setdefault(session.difficulty, [])
            .append(new_score))

    def get_scores(self, game: Game, difficulty: str, sort: bool = True) -> List[GameSession]:
        """Return a list of scores from the given game on the given difficulty.

        Returns:
            A list of sessions of games.
        """
        try:
            game_data = get_first_insensitive_key(self._data, game.game_name)
        except ValueError:
            raise MissingConfigKeyError("The game '{0}' was not found".format(game.game_name), game.game_name)

        try:
            difficulty_data = get_first_insensitive_key(game_data, difficulty)
        except ValueError:
            # There is no such difficulty. This shouldn't raise an exception, because it could just mean that the user
            # hasn't set any scores for that difficulty yet.
            return []

        scores = [
            GameSession(
                game,
                difficulty,
                username=score["username"],
                duration=score["duration"],
                completed=datetime.datetime.fromtimestamp(score["completed"]),
            )
            for score in difficulty_data
        ]

        if sort:
            scores.sort(key=lambda x: x.duration)

        return scores

    def get_high_score(self, game: Game, difficulty: str) -> Optional[GameSession]:
        """Get the score with the best time for the given game and difficulty.

        Returns:
            The session for the game with the high score or None if there are no scores.
        """
        try:
            return self.get_scores(game, difficulty, sort=True)[0]
        except IndexError:
            # There are no scores for the given game and difficulty.
            return None


class ScoreSort(enum.Enum):
    """A method of sorting game sessions.

    Attributes:
        column_name: The name of the column to sort by.
        key: The key function used for sorting.
    """
    USERNAME = ("Username", lambda x: x.username)
    SCORE = ("Score", lambda x: x.duration)
    DATE = ("Date", lambda x: x.completed)

    def __init__(self, column_name: str, key: Callable[[GameSession], Any]) -> None:
        self.column_name = column_name
        self.key = key

    @classmethod
    def from_name(cls, name: str) -> "ScoreSort":
        """Get a ScoreSort instance from its column name."""
        for difficulty in cls:
            if difficulty.name.lower() == name.lower():
                return difficulty


def format_scores(
        scores: List[GameSession], header: bool = True, header_style: Optional[str] = "bold",
        sort_method: Optional[ScoreSort] = None) -> Union[str, FormattedText]:
    """Format the given scores in a table.

    Args:
        scores: The scores to format.
        header: Print a header row containing a name for each column.
        header_style: The style to apply to the header row if there is one. If None, apply to style.
        sort_method: The method used to sort the scores. If None, then sort by score.

    Returns:
        A FormattedText instance if a header style is provided, and a str otherwise.
    """
    sort_method = sort_method or ScoreSort.SCORE
    output_header = [("#", "Username", "Score", "Date")]

    sorted_scores = sorted(scores, key=sort_method.key)
    output_data = [(
            str(i + 1),
            session.username,
            format_duration(session.duration),
            session.completed.strftime("%d %b %Y %H:%M")
        )
        for i, session in enumerate(sorted_scores)
    ]

    if not header:
        return format_table(output_data)
    elif header_style is None:
        return format_table(output_header + output_data)
    else:
        output_lines = format_table(output_header + output_data).splitlines()
        header_text = output_lines[0] + "\n"
        data_text = "\n".join(output_lines[1:])
        return FormattedText([(header_style, header_text), ("", data_text)])


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
    score_store = Scores()
    score_store.read()

    # Inform the user if they've set a new high score.
    high_score = score_store.get_high_score(session.game, session.difficulty)
    if high_score is None or session.duration < high_score.duration:
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
