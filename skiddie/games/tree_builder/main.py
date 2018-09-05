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
import random

from skiddie.games.tree_builder.gui import GameInterface
from skiddie.games.tree_builder.constants import NODE_VALUE_SETS
from skiddie.games.tree_builder.logic import TreeNode, ClosureTable
from skiddie.utils.ui import print_correct_message


def play(challenges_to_win: int, tree_depth: int, min_branches: int, max_branches: int, total_nodes: int) -> None:
    """Play the game.

    Args:
        challenges_to_win: The number of trees that need to be completed to win the game. Increasing this makes the
            game more difficult.
        tree_depth: The number of levels in the generated tree. Increasing this makes the game more difficult.
        min_branches: The minimum number of branches at each level of the tree. The effect on the difficulty varies.
        max_branches: The maximum number of branches at each level of the tree. The effect on the difficulty varies.
        total_nodes: The number of nodes that the tree will have. Increasing this makes the game more difficult.
    """
    for _ in range(challenges_to_win):
        tree = TreeNode.create_random(tree_depth, min_branches, max_branches, total_nodes, random.choice(NODE_VALUE_SETS))
        closure_table = ClosureTable(tree)

        interface = GameInterface(tree, closure_table)
        interface.app.run()

    print_correct_message()
