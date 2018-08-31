"""Code for generating random trees.

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
import abc
import random
from typing import List, Optional


class TreeNode(abc.ABC):
    """A node in a tree of strings that can be formatted.

    Attributes:
        value: The value of the node.
        parent: The parent node.
        children: The children of the node.
        VERTICAL_STRING: The string used as a vertical line when formatting the tree.
        TEE_STRING: The string used as a tee when formatting the tree.
        ANGLE_STRING: The string used as a right angle when formatting the tree.
    """
    VERTICAL_STRING = "│"
    TEE_STRING = "├─"
    ANGLE_STRING = "└─"

    def __init__(self, value: str, parent: Optional["TreeNode"] = None, children: List["TreeNode"] = None) -> None:
        self.value = value
        self.parent = parent
        self.children = children or []

    def add_child(self, value: str) -> "TreeNode":
        """Add a child to this node and return it."""
        new_node = TreeNode(value, parent=self)
        self.children.append(new_node)
        return new_node

    def __repr__(self) -> str:
        return "TreeNode('{0}')".format(self.value)

    @property
    def descendants(self) -> List["TreeNode"]:
        """A list of all the descendants of this node.

        The returned nodes are in depth-first order.
        """
        def walk_nodes(node: "TreeNode") -> List["TreeNode"]:
            nodes = [node]
            for child in node.children:
                nodes += walk_nodes(child)
            return nodes

        return walk_nodes(self)

    @property
    def ancestors(self) -> List["TreeNode"]:
        """A list of all the ancestors of this node.

        More immediate ancestors come before more distant ancestors.
        """
        current_node = self
        output = []

        while current_node.parent is not None:
            current_node = current_node.parent
            output.append(current_node)

        return output

    @property
    def root_node(self) -> "TreeNode":
        """The root node in the tree."""
        try:
            return self.ancestors[-1]
        except IndexError:
            # This node is the root node.
            return self

    @property
    def _is_last_child(self) -> bool:
        """Whether this node is the last child of its parent.

        For the root node, this returns True.
        """
        try:
            return self is self.parent.children[-1]
        except AttributeError:
            return True

    @property
    def _siblings(self) -> List["TreeNode"]:
        """All the other children of this node's parent."""
        siblings = self.parent.children
        siblings.remove(self)
        return siblings

    def format_tree(self, hide_values=False) -> str:
        """Format the tree as a string.

        Args:
            hide_values: Do not show the value for each node.
        """
        root_node = self.root_node
        root_value = "" if hide_values else root_node.value
        descendants = self.descendants[1:]
        lines = []

        for i, descendant in enumerate(descendants):
            new_line = ""

            # Add the vertical lines. No vertical lines or spaces should be added for the root node.
            for ancestor in reversed(descendant.ancestors[:-1]):
                new_line += "  " if ancestor._is_last_child else "{0} ".format(self.VERTICAL_STRING)

            # Add a tee or right angle.
            new_line += self.ANGLE_STRING if descendant._is_last_child else self.TEE_STRING

            # Add the value of the node.
            new_line += "" if hide_values else descendant.value

            lines.append(new_line)

        return "\n".join([root_value, *lines])

    @classmethod
    def create_random(
            cls, depth: int, min_branches: int, max_branches: int, num_nodes: int,
            possible_values: List[str]) -> "TreeNode":
        """Create a random tree that follows the given parameters.

        Args:
            depth: The number of levels in the generated tree.
            min_branches: The minimum number of branches at each level of the tree.
            max_branches: The maximum number of branches at each level of the tree.
            num_nodes: The number of nodes that the tree should have.
            possible_values: The pool of values to select values from.
        """
        value_pool = possible_values.copy()
        random.shuffle(value_pool)

        def create_tree(node: TreeNode, current_depth: int = 0) -> None:
            if current_depth >= depth:
                return

            total_nodes = len(root_node.descendants)
            remaining_nodes = num_nodes - total_nodes

            # Get the minimum and maximum number of possible descendants that this node can have.
            remaining_levels = depth - current_depth
            min_possible_descendants = sum(min_branches**i for i in range(1, remaining_levels+1))
            max_possible_descendants = sum(max_branches**i for i in range(1, remaining_levels+1))

            # Get the minimum and maximum number of descendants that each child of this node could have.
            min_descendants_per_child = round(min_possible_descendants / min_branches)
            max_descendants_per_child = round(max_possible_descendants / max_branches)

            # Get the range of numbers of children that this node can have. Shuffle them to avoid bias in which one is
            # chosen.
            possible_children = list(range(min_branches, max_branches+1))
            random.shuffle(possible_children)

            # Determine how many children this node should have. Look at the minimum and maximum number of descendants
            # that this node could have with a given number of children.
            children_to_add = 0
            for num_children in possible_children:
                range_min = min_descendants_per_child * num_children
                range_max = max_descendants_per_child * num_children
                if remaining_nodes in range(range_min, range_max+1):
                    children_to_add = num_children
                    break

            # Add children to the node.
            for _ in range(children_to_add):
                node.add_child(value_pool.pop())

            # Add children to this node's children.
            for child in node.children:
                create_tree(child, current_depth+1)

        root_node = TreeNode(value_pool.pop())
        create_tree(root_node)

        return root_node
