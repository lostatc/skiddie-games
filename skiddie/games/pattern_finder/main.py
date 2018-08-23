"""A game about finding patterns in randomly generated numbers.

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
import time
import random

from skiddie.games.pattern_finder.logic import PatternGrid
from skiddie.games.pattern_finder.gui import GameInterface
from skiddie.utils.ui import print_banner

# The proportion of cells in the grid that are turned on.
GRID_COVERAGE = 0.5


def play(
        challenges_to_win: int, grid_width: int, grid_height: int, choices: int, cells_to_flip: int,
        incorrect_penalty: float) -> None:
    """Play the game.

    Args:
        challenges_to_win: The number of challenges the user has to complete to win the game. Increasing this makes the
            game more difficult.
        grid_width: The number of columns in the grid. Increasing this makes the game more difficult.
        grid_height: The number of rows in the grid. Increasing this makes the game more difficult.
        choices: The number of possible solutions the user has to choose from. Increasing this makes the game more
            difficult.
        cells_to_flip: The number of cells to flip the state of for each false solution. Decreasing this makes the game
            more difficult.
        incorrect_penalty: The number of seconds to make the user wait after an incorrect answer. Increasing this makes
            the game more difficult.
    """
    completed_challenges = 0

    while completed_challenges < challenges_to_win:
        # Generate the challenge grid and the solutions grids.
        challenge_grid = PatternGrid.create_random(grid_width, grid_height, GRID_COVERAGE)
        solution_grids = [PatternGrid.create_negative(challenge_grid) for _ in range(choices)]

        # Scramble all but one of the solutions.
        for i in range(choices - 1):
            solution_grids[i].scramble(cells_to_flip)
        random.shuffle(solution_grids)

        # Prompt the user.
        interface = GameInterface(challenge_grid, solution_grids)
        selected_grid = interface.app.run()

        # Check the user's answer.
        if selected_grid.check_negative(challenge_grid):
            completed_challenges += 1
        else:
            print_banner("INCORRECT", style="ansired bold")
            time.sleep(incorrect_penalty)

    print_banner("ACCESS GRANTED", style="ansigreen bold")
