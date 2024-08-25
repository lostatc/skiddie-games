"""Code for generating random trees.

Copyright 2017-2020 Wren Powell <wrenp@duck.com>

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
import collections
import copy
import random
from typing import List, Optional, NamedTuple

from prompt_toolkit.formatted_text import FormattedText

from skiddie.utils.ui import format_table_columns

# The maximum number of rows in each column of the formatted closure table.
MAX_TABLE_ROWS = 35


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
    def depth(self) -> int:
        """The number of levels deep this node is."""
        return len(self.ancestors)

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

    def format_tree(self, hide_values=False) -> str:
        """Format the tree as a string.

        The order that the nodes appear in the output is the same as the order they appear in `self.descendants`.

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

    def __eq__(self, other: "TreeNode") -> bool:
        """Return whether the two nodes have the same value."""
        return self.value == other.value

    def __lt__(self, other: "TreeNode") -> bool:
        return self.value < other.value

    def __gt__(self, other: "TreeNode") -> bool:
        return self.value > other.value

    def equivalent_to(self, other: "TreeNode") -> bool:
        """Return whether this tree is equivalent to `other`.

        The two trees are equivalent if each node in each tree has the same children.
        """
        if self != other:
            return False

        # Iterate through both trees depth-first.
        node_stack = collections.deque([(self, other)])
        while node_stack:
            self_node, other_node = node_stack.pop()

            # The order of the children should not matter.
            self_children, other_children = sorted(self_node.children), sorted(other_node.children)

            if self_children != other_children:
                return False

            for self_child, other_child in zip(self_children, other_children):
                node_stack.append((self_child, other_child))

        return True

    def copy_with_values(self, values: List[str]) -> "TreeNode":
        """Create a copy of this tree, substituting the values if its descendants for the given ones."""
        new_tree = copy.deepcopy(self)
        for node, value in zip(new_tree.descendants, values):
            node.value = value

        return new_tree

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

        root_node = TreeNode(value_pool.pop())

        def create_minimum_tree(node: TreeNode) -> None:
            """Create a new child of the given node with the minimum possible number of branches and levels."""
            min_children = max(1, min_branches)

            # Don't add the child if it would violate the constraints.
            if len(node.children) >= max_branches:
                return
            if node.depth >= depth:
                return
            if len(node.root_node.descendants) >= num_nodes:
                return

            # Add the minimum possible number of children to the node.
            new_children = []
            for _ in range(min_children):
                new_child = node.add_child(value_pool.pop())
                new_children.append(new_child)

            # Recursively add children.
            for child in new_children:
                create_minimum_tree(child)

        def get_random_node(node: TreeNode) -> TreeNode:
            """Get a random descendant of the given node.

            Each branch has an equal probability of being selected regardless of how many nodes it has. This is to make
            the nodes in the resulting tree more evenly distributed.
            """
            stop_depth = random.randint(0, depth)
            current_node = node

            while current_node.depth < stop_depth:
                current_node = random.choice(current_node.children)

            return current_node

        create_minimum_tree(root_node)

        # Randomly add new branches to the tree until the required number of nodes is met.
        while len(root_node.descendants) < num_nodes:
            random_node = get_random_node(root_node)
            create_minimum_tree(random_node)

        return root_node


ClosureTableRow = NamedTuple(
    "ClosureTableRow",
    [("ancestor", TreeNode), ("descendant", TreeNode), ("distance", int)]
)


class ClosureTable:
    """An in-code representation of a closure table as used in databases.

    Attributes:
        tree: The tree that the closure table is based on.
    """
    def __init__(self, tree: TreeNode) -> None:
        self.tree = tree

    @property
    def table(self) -> List[ClosureTableRow]:
        """The closure table."""
        output = []

        for ancestor_node in self.tree.descendants:
            for descendant_node in ancestor_node.descendants:
                distance = descendant_node.depth - ancestor_node.depth
                new_row = ClosureTableRow(ancestor_node, descendant_node, distance)
                output.append(new_row)

        return output

    def format_table(self, shuffle_rows: bool = True, header_style: str = "bold") -> FormattedText:
        """Return a formatted string representation of the table.

        Args:
            shuffle_rows: Shuffle the rows of the table before formatting them. Rows are still grouped by their
                ancestor.
            header_style: The style to apply to the header row.
        """
        table_header = ("Ancestor", "Descendant", "Distance")
        table_data = [
            (ancestor.value, descendant.value, str(distance))
            for ancestor, descendant, distance in self.table
        ]

        # Shuffle the rows.
        if shuffle_rows:
            random.shuffle(table_data)
            table_data.sort(key=lambda x: x[0])

        # Format the table.
        formatted_rows = format_table_columns(table_data, MAX_TABLE_ROWS, header=table_header).splitlines()

        # Convert to formatted text.
        header_row = formatted_rows[0] + "\n"
        data_rows = "\n".join(formatted_rows[1:])
        style_tuples = [
            (header_style, header_row),
            ("", data_rows),
        ]

        return FormattedText(style_tuples)
