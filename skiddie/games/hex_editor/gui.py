"""Code for the game's UI.

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
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.filters import is_done
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import FloatContainer, HSplit, BufferControl, Layout, Window, ConditionalContainer
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.widgets import Label, HorizontalLine, ValidationToolbar

from skiddie.utils import Screen, MultiScreenApp
from skiddie.constants import GUI_STYLE
from skiddie.games.hex_editor.generator import MazeGrid


class CoordinateValidator(Validator):
    """Validate whether the given coordinates are valid."""
    def __init__(self, maze_grid: MazeGrid):
        self._maze_grid = maze_grid

    def validate(self, document: Document) -> None:
        text = document.text

        try:
            tile = self._maze_grid.get_from_user_string(text)
        except ValueError as e:
            raise ValidationError(message=str(e), cursor_position=len(text))

        if tile.visited:
            raise ValidationError(message="This tile has already been visited", cursor_position=len(text))

        if not self._maze_grid.check_visitable(tile):
            raise ValidationError(message="This tile is not next a valid tile", cursor_position=len(text))


class MazeScreen(Screen):
    """The screen used for displaying the maze and allowing the user to interact with it."""
    def __init__(self, multi_screen: MultiScreenApp, maze_grid: MazeGrid) -> None:
        self.maze_grid = maze_grid
        super().__init__(multi_screen)

    def get_root_container(self) -> FloatContainer:
        validator = CoordinateValidator(self.maze_grid)

        return FloatContainer(
            HSplit([
                Label(
                    text=self.maze_grid.format_grid,
                ),
                HorizontalLine(),
                Window(
                    BufferControl(
                        buffer=Buffer(
                            validator=validator,
                            validate_while_typing=False,
                            multiline=False,
                            accept_handler=self._accept_handler,
                        ),
                        input_processors=[
                            BeforeInput("Enter coordinates (x, y): "),
                        ],
                    ),
                ),
                ConditionalContainer(
                    ValidationToolbar(),
                    filter=~is_done,
                ),
            ]),
            floats=[],
        )

    def _accept_handler(self, buffer: Buffer) -> None:
        """Visit the tile at the given coordinates."""
        # The validator has already checked that these coordinates are valid.
        coordinates = buffer.document.text
        tile = self.maze_grid.get_from_user_string(coordinates)
        tile.visit()

        if self.maze_grid.check_complete():
            self.multi_screen.app.exit()
        else:
            buffer.reset()


class GameInterface(MultiScreenApp):
    """The UI for playing the game."""
    def __init__(self, maze_grid: MazeGrid) -> None:
        self._maze_screen = MazeScreen(self, maze_grid)
        self._global_keybindings = self._create_global_keybindings()

        layout = Layout(container=self._maze_screen.get_root_container())

        app = Application(layout, style=GUI_STYLE, key_bindings=self._global_keybindings)

        super().__init__(app, self._maze_screen)

    @staticmethod
    def _create_global_keybindings() -> KeyBindings:
        bindings = KeyBindings()

        bindings.add("c-c")(lambda event: event.app.exit(exception=KeyboardInterrupt))

        return bindings
