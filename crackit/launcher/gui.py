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
import functools
import collections
from typing import Dict, Optional

from prompt_toolkit import Application
from prompt_toolkit.layout.containers import VSplit, HSplit
from prompt_toolkit.widgets import Button, Frame, Label, HorizontalLine
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import Container, DynamicContainer
from prompt_toolkit.key_binding import KeyBindings

from crackit.launcher.common import Game, GAME_HASH_CRACKER, GAME_SHELL_SCRIPTER


class Launcher:
    """A GUI application for launching games.

    Attributes:
        application: The application object for the GUI launcher.
        _selected_game: The game which was has been selected on the game selection screen.
    """
    def __init__(self):
        self._selected_game = None
        self.application = self._create_application()

    @property
    @functools.lru_cache()
    def _global_keybindings(self) -> KeyBindings:
        """The global keybindings."""
        bindings = KeyBindings()

        @bindings.add("c-c")
        @bindings.add("q")
        def _exit(event):
            event.app.exit()

        return bindings

    @property
    @functools.lru_cache()
    def _button_keybindings(self) -> KeyBindings:
        """The keybindings for windows containing buttons."""
        bindings = KeyBindings()
        bindings.add("down")(focus_next)
        bindings.add("up")(focus_previous)
        return bindings

    @property
    @functools.lru_cache()
    def _game_buttons(self) -> Dict[Button, Game]:
        """A map of buttons to the games they represent."""
        return collections.OrderedDict([(
                Button("hash_cracker", width=20, handler=lambda: self._set_active_container(GAME_HASH_CRACKER)),
                GAME_HASH_CRACKER
            ), (
                Button("shell_scripter", width=20, handler=lambda: self._set_active_container(GAME_SHELL_SCRIPTER)),
                GAME_SHELL_SCRIPTER
            ),
        ])

    @property
    @functools.lru_cache()
    def _layout(self) -> Layout:
        # root_container = DynamicContainer(self._get_active_container)
        # return Layout(container=root_container)
        return Layout(container=self._game_select_container)

    @property
    @functools.lru_cache()
    def _game_select_container(self) -> Container:
        """The layout for selecting a game."""
        container = VSplit([
            Frame(
                HSplit([
                        *self._game_buttons.keys(),
                        HorizontalLine(),
                        Button("Quit", width=20, handler=self._exit),
                    ],
                    width=Dimension(min=20, max=40),
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

        return container

    @property
    @functools.lru_cache()
    def _game_option_container(self) -> Container:
        """The layout for configuring options for a game."""
        container = VSplit([
            Frame(
                HSplit([
                    Button("Play", width=20),
                    Button("Difficulty", width=20),
                    Button("High Scores", width=20),
                    HorizontalLine(),
                    Button("Back", width=20, handler=lambda: self._set_active_container(None)),
                ],
                    width=Dimension(min=20, max=40),
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

        return container

    def _create_application(self) -> Application:
        """Create the application."""
        return Application(
            layout=self._layout,
            full_screen=True,
            mouse_support=True,
            key_bindings=self._global_keybindings
        )

    def _set_active_container(self, game: Optional[Game]) -> None:
        """Set the currently active container based on the selected game."""
        self._selected_game = game

        if self._selected_game is None:
            active_container = self._game_select_container
        else:
            active_container = self._game_option_container

        self._layout.container = active_container
        self._layout.focus(active_container)

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
