"""A game about building trees from a closure table.

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


def main(challenges_to_win: int, tree_depth: int, min_branches: int, max_branches: int) -> None:
    """Play the game.

    Args:
        challenges_to_win: The number of trees that need to be completed to win the game. Increasing this makes the
            game more difficult.
        tree_depth: The number of levels in the generated tree. Increasing this makes the game more difficult.
        min_branches: The minimum number of branches at each level of the tree. Increasing this makes the game more difficult.
        max_branches: The maximum number of branches at each level of the tree. Increasing this makes the game more difficult.
    """
