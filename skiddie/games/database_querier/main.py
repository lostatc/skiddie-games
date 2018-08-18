"""A game about querying database tables.

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
from skiddie.games.database_querier.table import Table
from skiddie.games.database_querier.gui import GameInterface
from skiddie.utils import print_banner


def play(challenges_to_win: int, table_rows: int, table_columns: int) -> None:
    """Play the game.

    Args:
        challenges_to_win: The number of challenges the user has to complete to win the game. Increasing this makes the
            game more difficult.
        table_rows: The number of rows in the table. Increasing this makes the game more difficult.
        table_columns: The number of columns in the table. Increasing this makes the game more difficult.
    """
    completed_challenges = 0

    while completed_challenges < challenges_to_win:
        table = Table(table_rows, table_columns)
        table.create_table()

        # Prompt the user.
        interface = GameInterface(table)
        answer_is_correct = interface.app.run()

        if answer_is_correct:
            completed_challenges += 1
        else:
            print_banner("INCORRECT", style="ansired bold")

    print_banner("ACCESS GRANTED", style="ansigreen bold")
