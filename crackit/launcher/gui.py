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
from typing import Callable

from prompt_toolkit import Application
from prompt_toolkit.document import Document
from prompt_toolkit.layout.containers import VSplit, HSplit
from prompt_toolkit.widgets import Button, Frame, Label, HorizontalLine, Dialog, RadioList, Box, TextArea
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import FloatContainer, Window
from prompt_toolkit.filters import to_filter
from prompt_toolkit.key_binding import KeyBindings

from crackit.launcher.scores import Scores
from crackit.constants import GUI_STYLE
from crackit.utils import Screen, FloatScreen, MultiScreenApp
from crackit.launcher.common import Difficulty, Game, GameSession, GAMES
from crackit.launcher.scores import process_result, format_scores

# The width of buttons that are used to create menus.
MENU_BUTTON_WIDTH = 20


class GameSelectScreen(Screen):
    """The screen used for selecting a game to play.

    Args:
        menu_keybindings: The keybindings for interactive menus.

    Attributes:
        _menu_keybindings: The keybindings for interactive menus.
        _selected_game: The currently selected game.
        _game_options_screen: The screen for configuring options for the selected game.
        _game_buttons: A map of buttons to the games they represent. These buttons are used to access the options menu
            for each game.

    """
    def __init__(self, multi_screen: MultiScreenApp, menu_keybindings: KeyBindings) -> None:
        self._menu_keybindings = menu_keybindings

        self._selected_game = None

        self._game_options_screen = GameOptionsScreen(multi_screen, menu_keybindings, lambda: self._selected_game)

        self._game_buttons = collections.OrderedDict([(
                Button(
                    game.game_name, width=MENU_BUTTON_WIDTH,
                    handler=functools.partial(self._select_game, game),
                ),
                game
            )
            for game in sorted(GAMES, key=lambda x: x.game_name)
        ])

        super().__init__(multi_screen)

    def get_root_container(self) -> FloatContainer:
        return FloatContainer(
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

    def _select_game(self, game: Game) -> None:
        """Set the currently selected game and switch the active screen to the game selection screen."""
        self._selected_game = game
        self.multi_screen.set_screen(self._game_options_screen)

    # TODO: Find a way to wrap the output of this to fit the size of the window.
    def _get_game_description(self) -> str:
        """Return the correct description for the selected game.

        Returns:
            The description to display.
        """
        for key, value in self._game_buttons.items():
            if self.multi_screen.app.layout.has_focus(key):
                return value.description
        return ""

    def _exit(self) -> None:
        """Exit the application."""
        self.multi_screen.app.exit()


class GameOptionsScreen(Screen):
    """The screen used for configuring the options for a game.

    Args:
        menu_keybindings: The keybindings for interactive menus.
        selected_game_getter: A function which returns the game which is currently selected.
                ),
                Frame(
                    HSplit([
                        Box(

    Attributes:
        _menu_keybindings: The keybindings for interactive menus.
        _selected_game_getter: A function which returns the game which is currently selected.
        _selected_difficulties: A map of games to their currently selected difficulties.
        _difficulty_select_screen: The screen used for setting the difficulty of the selected game.
    """
    def __init__(
            self, multi_screen: MultiScreenApp, menu_keybindings: KeyBindings,
            selected_game_getter: Callable[[], Game]) -> None:
        self._menu_keybindings = menu_keybindings

        def selected_difficulty_setter(value: Difficulty) -> None:
            self._selected_difficulty = value

        self._selected_game_getter = selected_game_getter
        self._selected_difficulties = {game: Difficulty.NORMAL for game in GAMES}

        self._difficulty_select_screen = DifficultySelectScreen(multi_screen, selected_difficulty_setter)
        self._high_score_screen = HighScoreScreen(
            multi_screen, menu_keybindings, lambda: self._selected_game, lambda: self._selected_difficulty
        )

        super().__init__(multi_screen)

    def get_root_container(self) -> FloatContainer:
        return FloatContainer(
            VSplit([
                Frame(
                    HSplit([
                            Button("Play", width=MENU_BUTTON_WIDTH, handler=self._return_session),
                            Button(
                                "Difficulty", width=MENU_BUTTON_WIDTH,
                                handler=lambda: self.multi_screen.add_floating_screen(self._difficulty_select_screen),
                            ),
                            Button(
                                "High Scores", width=MENU_BUTTON_WIDTH,
                                handler=lambda: self.multi_screen.set_screen(self._high_score_screen)
                            ),
                            HorizontalLine(),
                            Button(
                                "Back", width=MENU_BUTTON_WIDTH,
                                handler=self.multi_screen.set_previous,
                            ),
                        ],
                        width=Dimension(min=MENU_BUTTON_WIDTH, max=40),
                        height=Dimension(),
                    ),
                    title="Options",
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
                                text=self._selected_game.description,
                                dont_extend_height=False,
                                width=Dimension(min=40),
                            ),
                            padding=0,
                            padding_left=1,
                        ),
                    ]),
                    title=self._selected_game.game_name,
                ),
            ]),
            floats=[]
        )

    @property
    def _selected_difficulty(self) -> Difficulty:
        """The selected difficulty for the currently selected game."""
        return self._selected_difficulties[self._selected_game]

    @_selected_difficulty.setter
    def _selected_difficulty(self, value: Difficulty) -> None:
        """Set the selected difficulty for the currently selected game."""
        self._selected_difficulties[self._selected_game] = value

    @property
    def _selected_game(self) -> Game:
        """The currently selected game."""
        return self._selected_game_getter()

    def _return_session(self) -> None:
        """Exit the application and have it return the currently selected game with its selected difficulty."""
        self.multi_screen.app.exit(
            result=GameSession(self._selected_game, self._selected_difficulty)
        )


class DifficultySelectScreen(FloatScreen):
    """The screen used for setting the difficulty of a game.

    Attributes:
        _selected_difficulty_setter: A function which sets the difficulty for the currently selected game.
    """
    def __init__(
            self, multi_screen: MultiScreenApp,
            selected_difficulty_setter: Callable[[Difficulty], None]) -> None:
        self._selected_difficulty_setter = selected_difficulty_setter
        super().__init__(multi_screen)

    def get_root_container(self) -> Dialog:
        difficulty_radiolist = RadioList([
            (Difficulty.EASY, Difficulty.EASY.value),
            (Difficulty.NORMAL, Difficulty.NORMAL.value),
            (Difficulty.HARD, Difficulty.HARD.value),
        ])

        def ok_handler() -> None:
            self._selected_difficulty_setter(difficulty_radiolist.current_value)
            self.multi_screen.clear_floating()

        def cancel_handler() -> None:
            self.multi_screen.clear_floating()

        return Dialog(
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


class HighScoreScreen(Screen):
    """The screen used to display high scores.

    Args:
        selected_game_getter: A function which returns the game which is currently selected.
        selected_difficulty_getter: A function which returns the currently selected difficulty.

    Attributes:
        _menu_keybindings: The keybindings for interactive menus.
        _selected_game_getter: A function which returns the game which is currently selected.
        _selected_difficulty_getter: A function which returns the currently selected difficulty.
    """
    def __init__(
            self, multi_screen: MultiScreenApp, menu_keybindings: KeyBindings,
            selected_game_getter: Callable[[], Game], selected_difficulty_getter: Callable[[], Difficulty]) -> None:
        self._menu_keybindings = menu_keybindings
        self._selected_game_getter = selected_game_getter
        self._selected_difficulty_getter = selected_difficulty_getter
        super().__init__(multi_screen)

    def get_root_container(self) -> FloatContainer:
        score_store = Scores()
        score_store.read()
        high_scores = score_store.get_scores(self._selected_game, self._selected_difficulty)
        score_table = format_scores(high_scores)

        text_area = TextArea(
            text=score_table,
            read_only=True,
            scrollbar=True,
        )

        text_area.window.cursorline = to_filter(True)

        return FloatContainer(
            VSplit([
                Frame(
                    HSplit([
                            Button("Back", width=MENU_BUTTON_WIDTH, handler=self.multi_screen.set_previous),
                        ],
                        width=Dimension(min=MENU_BUTTON_WIDTH, max=40),
                        height=Dimension(),
                    ),
                    title="High Scores",
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
                            text_area,
                            padding=0,
                            padding_left=1,
                        ),
                    ]),
                    title=self._selected_game.game_name,
                ),
            ]),
            floats=[],
        )

    @property
    def _selected_game(self) -> Game:
        """The currently selected game."""
        return self._selected_game_getter()

    @property
    def _selected_difficulty(self) -> Difficulty:
        """The currently selected difficulty."""
        return self._selected_difficulty_getter()


class Launcher(MultiScreenApp):
    """A GUI application for launching games.

    Attributes:
        _global_keybindings: The application-wide keybindings.
        _menu_keybindings: The keybindings for windows containing button menus.
        _game_select_screen: The screen used for selecting a game to play.
    """
    def __init__(self) -> None:
        self._global_keybindings = self._create_global_keybindings()
        self._menu_keybindings = self._create_menu_keybindings()
        self._game_select_screen = GameSelectScreen(self, self._menu_keybindings)

        # Define layout.
        layout = Layout(container=self._game_select_screen.get_root_container())

        # Define style.
        style = GUI_STYLE

        # Define application.
        app = Application(
            layout=layout,
            style=style,
            full_screen=True,
            mouse_support=True,
            key_bindings=self._global_keybindings
        )

        super().__init__(app, self._game_select_screen)

    @staticmethod
    def _create_global_keybindings() -> KeyBindings:
        """Create keybindings for the whole application."""
        bindings = KeyBindings()

        bindings.add("tab")(focus_next)
        bindings.add("s-tab")(focus_previous)

        @bindings.add("c-c")
        @bindings.add("q")
        def _exit(event):
            event.app.exit()

        return bindings

    @staticmethod
    def _create_menu_keybindings() -> KeyBindings:
        """Create keybindings for interactive menus."""
        bindings = KeyBindings()
        bindings.add("down")(focus_next)
        bindings.add("up")(focus_previous)

        return bindings


def main() -> None:
    """Run the launcher GUI and play the selected game."""
    launcher = Launcher()
    session = launcher.app.run()

    if session is None:
        return

    session.play()
    process_result(session)
