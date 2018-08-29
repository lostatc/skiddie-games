"""A game about querying database tables.

Copyright © 2017-2018 Wren Powell <wrenp@duck.com>

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
from skiddie.games.database_querier.table import Table
from skiddie.games.database_querier.gui import GameInterface
from skiddie.utils.ui import print_correct_message, print_incorrect_message


def play(challenges_to_win: int, rows: int, continuous_columns: int, discrete_columns: int) -> None:
    """Play the game.

    Args:
        challenges_to_win: The number of challenges the user has to complete to win the game. Increasing this makes the
            game more difficult.
        rows: The number of rows in the table. Increasing this makes the game more difficult.
        continuous_columns: The number of continuous columns in the table. These are columns that have a range of
            possible values. Increasing this makes the game more difficult.
        discrete_columns: The number of discrete columns in the table. These are columns that have a limited number of
            possible values. Increasing this makes the game more difficult. Increasing this relative to
            `continuous_columns` also makes the game more difficult.
    """
    completed_challenges = 0

    while completed_challenges < challenges_to_win:
        table = Table(rows, continuous_columns, discrete_columns)
        table.create_table()

        # Prompt the user.
        interface = GameInterface(table)
        answer_is_correct = interface.app.run()

        if answer_is_correct:
            completed_challenges += 1
        else:
            print_incorrect_message()

    print_correct_message()
