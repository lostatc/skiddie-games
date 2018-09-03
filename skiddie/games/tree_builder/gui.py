"""The game's UI.

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
import copy

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import FloatContainer, HSplit, VSplit, Dimension
from prompt_toolkit.widgets import Button, TextArea, Label, Box, Frame

from skiddie.constants import GUI_STYLE
from skiddie.games.tree_builder.logic import ClosureTable, TreeNode
from skiddie.utils.ui import Screen, MultiScreenApp

# This is the width of the text boxes that the user types the names of nodes into.
NODE_INPUT_WIDTH = 25


class TreeScreen(Screen):
    """The screen used for displaying the table and rules.

    Args:
        multi_screen: A reference to the MultiScreenApp containing this instance.
        tree: The tree that the user must complete.
        closure_table: The closure table to display to the user.

    Attributes:
        tree: The tree that the user must complete.
        closure_table: The closure table to display to the user.
        node_inputs: A list of text areas where the user types in the name of each node. The order of these corresponds
            to the order that the nodes are returned from `TreeNode.descendants` in.
    """
    def __init__(self, multi_screen: MultiScreenApp, tree: TreeNode, closure_table: ClosureTable) -> None:
        self.tree = tree
        self.closure_table = closure_table
        self.node_inputs = []
        super().__init__(multi_screen)

    def get_root_container(self) -> FloatContainer:
        tree_lines = self.tree.format_tree(hide_values=True).splitlines()
        self.node_inputs = [
            TextArea(wrap_lines=False, style="class:tree-node", width=NODE_INPUT_WIDTH)
            for _ in self.tree.descendants
        ]
        tree_labels = [
            Label(line, dont_extend_width=True)
            for line in tree_lines
        ]

        tree_input_container = Frame(
            HSplit([
                VSplit([
                    label, button
                ])
                for label, button in zip(tree_labels, self.node_inputs)
            ]),
            title="Tree",
        )

        buttons = [
            Button("Done", handler=self.handle_input_confirm),
        ]

        button_container = Box(VSplit(buttons, padding=4), padding_top=1)

        tree_panel_container = Box(
            HSplit([
                tree_input_container,
                button_container,
            ])
        )

        table_container = Label(self.closure_table.format_table())

        root_container = FloatContainer(
            VSplit([tree_panel_container, table_container]),
            floats=[],
        )

        return root_container

    def handle_input_confirm(self) -> None:
        """This is called when the user confirms their input."""
        input_values = [text_area.text for text_area in self.node_inputs]
        input_tree = copy.deepcopy(self.tree)
        for node, value in zip(input_tree.descendants, input_values):
            node.value = value

        if self.tree.equivalent_to(input_tree):
            return self.multi_screen.app.exit()


class GameInterface(MultiScreenApp):
    """The UI for playing the game."""
    def __init__(self, tree: TreeNode, closure_table: ClosureTable) -> None:
        self._tree_screen = TreeScreen(self, tree, closure_table)
        self._global_keybindings = self._create_global_keybindings()

        app = Application(style=GUI_STYLE, key_bindings=self._global_keybindings)

        super().__init__(app, self._tree_screen)

    @staticmethod
    def _create_global_keybindings() -> KeyBindings:
        bindings = KeyBindings()

        bindings.add("c-c")(lambda event: event.app.exit(exception=KeyboardInterrupt))
        bindings.add("tab")(focus_next)
        bindings.add("down")(focus_next)
        bindings.add("s-tab")(focus_previous)
        bindings.add("up")(focus_previous)

        return bindings
