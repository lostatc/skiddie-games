"""The GUI for the game launcher.

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
import collections

from prompt_toolkit import Application
from prompt_toolkit.layout.containers import VSplit, HSplit
from prompt_toolkit.widgets import Button, Frame, Label, HorizontalLine
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import Container
from prompt_toolkit.key_binding import KeyBindings

from crackit.launcher.common import Difficulty, Game, GAME_HASH_CRACKER, GAME_SHELL_SCRIPTER

# The width of buttons that are used to create menus.
MENU_BUTTON_WIDTH = 20

# A list of all available games.
GAMES = ["GAME_HASH_CRACKER", "GAME_SHELL_SCRIPTER"]


class Launcher:
    """A GUI application for launching games.

    Attributes:
        _selected_game: The game which was has been selected on the game selection screen.
        _global_keybindings: The keybindings for the whole application.
        _button_keybindings: The keybindings for windows containing buttons.
        _game_buttons: A map of buttons to the games they represent.
        _game_select_container: The container for selecting a game.
        _game_option_container: The container for configuring options for a game.
        _layout: The layout for the application.
        application: The application object for the GUI launcher.
    """
    def __init__(self):
        self._selected_game = None

        # Define global keybindings.
        self._global_keybindings = KeyBindings()

        @self._global_keybindings.add("c-c")
        @self._global_keybindings.add("q")
        def _exit(event):
            event.app.exit()

        # Define local keybindings.
        self._button_keybindings = KeyBindings()
        self._button_keybindings.add("down")(focus_next)
        self._button_keybindings.add("up")(focus_previous)

        # Define widgets.
        self._game_buttons = collections.OrderedDict([(
                Button(
                    "hash_cracker", width=MENU_BUTTON_WIDTH,
                    handler=lambda: self._select_game(GAME_HASH_CRACKER)
                ),
                GAME_HASH_CRACKER
            ), (
                Button(
                    "shell_scripter", width=MENU_BUTTON_WIDTH,
                    handler=lambda: self._select_game(GAME_SHELL_SCRIPTER)
                ),
                GAME_SHELL_SCRIPTER
            ),
        ])

        # Define containers.
        self._game_select_container = VSplit([
            Frame(
                HSplit([
                    *self._game_buttons.keys(),
                    HorizontalLine(),
                    Button("Quit", width=MENU_BUTTON_WIDTH, handler=self._exit),
                ],
                    width=Dimension(min=MENU_BUTTON_WIDTH, max=40),
                    height=Dimension(),
                ),
                title="Select a Game",
                key_bindings=self._button_keybindings,
            ),
            Frame(
                Label(
                    text=self._get_game_description,
                    dont_extend_height=False,
                    width=Dimension(min=40),
                ),
            ),
        ])

        self._game_option_container = VSplit([
            Frame(
                HSplit([
                        Button("Play", width=MENU_BUTTON_WIDTH),
                        Button("Difficulty", width=MENU_BUTTON_WIDTH),
                        Button("High Scores", width=MENU_BUTTON_WIDTH),
                        HorizontalLine(),
                        Button(
                            "Back", width=MENU_BUTTON_WIDTH,
                            handler=lambda: self._set_active_container(self._game_select_container)
                        ),
                    ],
                    width=Dimension(min=MENU_BUTTON_WIDTH, max=40),
                    height=Dimension(),
                ),
                title=lambda: self._selected_game.name,
                key_bindings=self._button_keybindings,
            ),
            Frame(
                Label(
                    text=lambda: self._selected_game.description,
                    dont_extend_height=False,
                    width=Dimension(min=40),
                ),
            ),
        ])

        # Define layout.
        self._layout = Layout(container=self._game_select_container)

        # Define application.
        self.application = Application(
            layout=self._layout,
            full_screen=True,
            mouse_support=True,
            key_bindings=self._global_keybindings
        )

    def _set_active_container(self, container: Container) -> None:
        """Set the currently active and focused container for the layout.

        Args:
            container: The container to set as the active container.
        """
        self._layout.container = container
        self._layout.focus(container)

    def _select_game(self, game: Game) -> None:
        """Set the appropriate active container for a given game.

        This is called whenever a game is selected in the game selection menu.

        Args:
            game: The game that was selected.
        """
        self._selected_game = game

        if self._selected_game is None:
            self._set_active_container(self._game_select_container)
        else:
            self._set_active_container(self._game_option_container)

    # TODO: Find a way to wrap the output of this to fit the size of the window.
    def _get_game_description(self) -> str:
        """Return the correct description for the selected game.

        Returns:
            The description to display.
        """
        for key, value in self._game_buttons.items():
            if self._layout.has_focus(key):
                return value.description
        return ""

    def _exit(self) -> None:
        """Exit the application."""
        self.application.exit()


def main() -> None:
    """Run the GUI application."""
    launcher = Launcher()
    launcher.application.run()


if __name__ == "__main__":
    main()
