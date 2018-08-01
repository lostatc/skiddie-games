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
from prompt_toolkit import print_formatted_text

from crackit.utils import format_duration
from crackit.launcher.common import GameSession

# This is the string that immediately precedes the users time whenever their time is printed to stdout.
TIMER_RESULT_PREFIX = "Your time is: "


def process_result(session: GameSession, print_stdout: bool = True) -> None:
    """Process the duration that the user played a game for.

    Args:
        session: The session of the game to process the result of.
        print_stdout: Print the result to stdout.

    Raises:
        ValueError: A GameSession was passed in which had not been played yet.
    """
    if session.duration is None:
        raise ValueError("the game has not been played yet")

    if print_stdout:
        print_formatted_text(TIMER_RESULT_PREFIX + format_duration(session.duration))
