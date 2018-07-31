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

from prompt_toolkit import Application, print_formatted_text
from prompt_toolkit.layout.containers import VSplit, HSplit
from prompt_toolkit.widgets import Button, Frame, Label, HorizontalLine, Dialog, RadioList, Box
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import FloatContainer, Float
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from crackit.utils import format_duration
from crackit.launcher.common import Difficulty, Game, GAMES, GAME_HASH_CRACKER, GAME_SHELL_SCRIPTER

# The width of buttons that are used to create menus.
MENU_BUTTON_WIDTH = 20


class Launcher:
    """A GUI application for launching games.

    Attributes:
        _selected_game: The game which was has been selected on the game selection screen.
        _selected_difficulties: A map of games to their currently selected difficulties.
        _global_keybindings: The keybindings for the whole application.
        _menu_keybindings: The keybindings for interactive menus.
        _game_buttons: A map of buttons to the games they represent.
        _game_select_container: The container for selecting a game.
        _game_option_container: The container for configuring options for a game.
        _difficulty_select_container: The container for selecting a difficulty.
        _layout: The layout for the application.
        application: The application object for the GUI launcher.
    """
    def __init__(self):
        self._selected_game = None
        self._selected_difficulties = {game: Difficulty.NORMAL for game in GAMES}

        # Define global keybindings.
        self._global_keybindings = KeyBindings()

        @self._global_keybindings.add("c-c")
        @self._global_keybindings.add("q")
        def _exit(event):
            event.app.exit()

        # Define local keybindings.
        self._menu_keybindings = KeyBindings()
        self._menu_keybindings.add("down")(focus_next)
        self._menu_keybindings.add("up")(focus_previous)

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
        self._game_select_container = FloatContainer(
            VSplit([
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
                    key_bindings=self._menu_keybindings,
                ),
                Frame(
                    Box(
                        Label(
                            text=self._get_game_description,
                            dont_extend_height=False,
                            width=Dimension(min=40),
                        ),
                        padding=0,
                        padding_left=1,
                    ),
                ),
            ]),
            floats=[]
        )

        self._game_option_container = FloatContainer(
            VSplit([
                Frame(
                    HSplit([
                            Button("Play", width=MENU_BUTTON_WIDTH, handler=self._play_game),
                            Button(
                                "Difficulty", width=MENU_BUTTON_WIDTH,
                                handler=lambda: self._add_float(self._difficulty_select_container),
                            ),
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
                    key_bindings=self._menu_keybindings,
                ),
                Frame(
                    HSplit([
                        Box(
                            Label(
                                text=lambda: "Difficulty: {0}".format(self._selected_difficulty.value),
                                width=Dimension(min=40),
                            ),
                            padding=0,
                            padding_left=1,
                        ),
                        HorizontalLine(),
                        Box(
                            Label(
                                text=lambda: self._selected_game.description,
                                dont_extend_height=False,
                                width=Dimension(min=40),
                            ),
                            padding=0,
                            padding_left=1,
                        ),
                    ]),
                ),
            ]),
            floats=[]
        )

        difficulty_radiolist = RadioList([
            (Difficulty.EASY, Difficulty.EASY.value),
            (Difficulty.NORMAL, Difficulty.NORMAL.value),
            (Difficulty.HARD, Difficulty.HARD.value),
        ])

        def ok_handler() -> None:
            self._selected_difficulty = difficulty_radiolist.current_value
            self._clear_floats()

        def cancel_handler() -> None:
            self._clear_floats()

        self._difficulty_select_container = Dialog(
            title="Difficulty",
            body=HSplit([
                    Label(text="Select a difficulty", dont_extend_height=True),
                    difficulty_radiolist,
                ],
                padding=1,
            ),
            buttons=[
                Button(text="Okay", handler=ok_handler),
                Button(text="Cancel", handler=cancel_handler),
            ],
            with_background=True,
        )

        # Define layout.
        self._layout = Layout(container=self._game_select_container)

        # Define style.
        self._style = Style([
            ("button.focused", "bg:ansired"),
            ("dialog.body", "fg:ansiwhite bg:ansiblack"),
            ("dialog shadow", "bg:ansibrightblack"),
            ("dialog frame.label", "fg:ansigreen"),
        ])

        # Define application.
        self.application = Application(
            layout=self._layout,
            style=self._style,
            full_screen=True,
            mouse_support=True,
            key_bindings=self._global_keybindings
        )

    @property
    def _selected_difficulty(self) -> Difficulty:
        """The selected difficulty for the currently selected game."""
        return self._selected_difficulties[self._selected_game]

    @_selected_difficulty.setter
    def _selected_difficulty(self, value: Difficulty) -> None:
        """Set the selected difficulty for the currently selected game."""
        self._selected_difficulties[self._selected_game] = value

    def _set_active_container(self, container: FloatContainer) -> None:
        """Set the currently active and focused container for the layout.

        This requires a FloatContainer so that floats can always be added.

        Args:
            container: The container to set as the active container.
        """
        self._layout.container = container
        self._layout.focus(container)

    def _add_float(self, container) -> None:
        """Add a container to the current container as a float.

        Args:
            container: The container to add as a float.
        """
        self._layout.container.floats.append(Float(container))
        self._layout.focus(container)

    def _clear_floats(self) -> None:
        """Remove all floats from the current container."""
        self._layout.container.floats.clear()
        self._layout.focus(self._layout.container)

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

    def _play_game(self) -> None:
        """Play the currently selected game with its selected difficulty."""
        self.application.exit(
            result=lambda: self._selected_game.launcher(self._selected_difficulty)
        )

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
    """Run the launcher GUI and play the selected game."""
    launcher = Launcher()
    game_timer = launcher.application.run()

    if game_timer is None:
        return

    game_duration = game_timer()
    print_formatted_text("Your time is: {0}".format(format_duration(game_duration)))


if __name__ == "__main__":
    main()
