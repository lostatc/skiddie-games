"""The game's UI.

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
import functools

from prompt_toolkit import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout.containers import VSplit, HSplit
from prompt_toolkit.widgets import Frame, Label, HorizontalLine, Box, VerticalLine
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import FloatContainer
from prompt_toolkit.key_binding import KeyBindings

from skiddie.utils.ui import Screen, MultiScreenApp, SelectableLabel
from skiddie.constants import GUI_STYLE

from skiddie.games.database_querier.table import Table


class TableScreen(Screen):
    """The screen used for displaying the table and rules.

    Args:
        multi_screen: A reference to the MultiScreenApp containing this instance.
        table: The table to display in the interface.
    """
    def __init__(self, multi_screen: MultiScreenApp, table: Table) -> None:
        self.table = table
        super().__init__(multi_screen)

    def get_root_container(self) -> FloatContainer:
        header_row = self.table.format_table().splitlines()[0]
        data_rows = self.table.format_table().splitlines()[1:]

        row_buttons = [
            SelectableLabel(row, handler=functools.partial(self._handle_answer, i))
            for i, row in enumerate(data_rows)
        ]

        table_container = HSplit([
            Label(
                FormattedText([("class:column-name", header_row)]),
            ),
            HorizontalLine(),
            *row_buttons,
        ])

        rules_container = Box(
            Label(
                self.table.format_constraints(separator="\n\n"),
                dont_extend_width=True,
            ),
        )

        return FloatContainer(
            Box(
                Frame(
                    VSplit([
                        table_container,
                        VerticalLine(),
                        rules_container,
                    ])
                ),
            ),
            floats=[],
        )

    def _handle_answer(self, index: int) -> None:
        self.multi_screen.app.exit(result=index in self.table.overlapping_indices)


class GameInterface(MultiScreenApp):
    """The UI for playing the game."""
    def __init__(self, table: Table) -> None:
        self._table_screen = TableScreen(self, table)
        self._global_keybindings = self._create_global_keybindings()

        app = Application(style=GUI_STYLE, key_bindings=self._global_keybindings)

        super().__init__(app, self._table_screen)

    @staticmethod
    def _create_global_keybindings() -> KeyBindings:
        bindings = KeyBindings()

        bindings.add("c-c")(lambda event: event.app.exit(exception=KeyboardInterrupt))
        bindings.add("tab")(focus_next)
        bindings.add("down")(focus_next)
        bindings.add("s-tab")(focus_previous)
        bindings.add("up")(focus_previous)

        return bindings
