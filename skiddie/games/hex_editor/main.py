"""A game about editing binary data.

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
from skiddie.games.hex_editor.logic import MazeTile, MazeGrid
from skiddie.games.hex_editor.gui import GameInterface

from prompt_toolkit import print_formatted_text

from skiddie.utils.ui import print_correct_message


def play(
        grids_to_win: int, grid_width: int, grid_height: int,
        min_distance: int, max_distance: int, branch_probability: float) -> None:
    """Play the game.

    Args:
        grids_to_win: The number of grids that need to be completed to win the game. Increasing this makes the game more
            difficult.
        grid_width: The number of columns in the grid. Increasing this makes the game more difficult.
        grid_height: The number of rows in the grid. Increasing this makes the game more difficult.
        min_distance: The minimum length for a segment of the generated path through the maze grid. Decreasing this
            makes the game more difficult.
        max_distance: The maximum length for a segment of the generated path through the maze grid. Decreasing this
            makes the game more difficult.
        branch_probability: The probability for each tile that a dead end branch will be generated. Increasing this
            makes the game more difficult.
    """
    for _ in range(grids_to_win):
        grid = MazeGrid.create_random(
            grid_width, grid_height, min_distance, max_distance, branch_probability
        )

        interface = GameInterface(grid)
        interface.app.run()

    print_correct_message()
