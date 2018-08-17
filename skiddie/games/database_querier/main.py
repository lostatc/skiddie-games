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


def play(table_rows: int, table_columns: int, max_discrete_values: int) -> None:
    """Play the game.

    Args:
        table_rows: The number of rows in the table. Increasing this makes the game more difficult.
        table_columns: The number of columns in the table. Increasing this makes the game more difficult.
        max_discrete_values: The maximum number of unique discrete values per column. Increasing this makes the game
            more difficult.
    """
    table = Table(table_rows, table_columns)
    table.create_table(max_discrete_values)
    print(table.format_table())
    print(table.format_constraints())
    print(table.overlapping_indices)


play(20, 4, 2)
