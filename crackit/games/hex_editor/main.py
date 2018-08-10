"""A game about editing binary data.

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
from crackit.games.hex_editor.generator import MazeTile, MazeGrid
from crackit.games.hex_editor.gui import GameInterface

from prompt_toolkit import print_formatted_text

from crackit.utils import print_banner


def play(
        grids_to_win: int, grid_width: int, grid_height: int, forward_weight: int, sideways_weight: int,
        min_distance: int, max_distance: int) -> None:
    """Play the game.

    Args:
        grids_to_win: The number of grids that need to be completed to win the game.
        grid_width: The number of columns in the grid.
        grid_height: The number of rows in the grid.
        forward_weight: The relative weight given to forward moves when generating the path.
        sideways_weight: The relative weight given to sideways moves when generating the path.
        min_distance: The minimum length for a segment of the generated path through the maze grid.
        max_distance: The maximum length for a segment of the generated path through the maze grid.
    """
    for _ in range(grids_to_win):
        grid = MazeGrid.create_random(
            grid_width, grid_height, forward_weight, sideways_weight, min_distance, max_distance
        )

        interface = GameInterface(grid)
        interface.app.run()

    print_banner("ACCESS GRANTED", style="ansigreen bold")
