"""The UI for the game.

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
import functools
from typing import List

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import FloatContainer, HSplit, Window, WindowAlign, FormattedTextControl, Layout, Dimension, \
    VSplit
from prompt_toolkit.widgets import Label, HorizontalLine, Frame, Box, Button

from skiddie.constants import GUI_STYLE
from skiddie.games.pattern_finder.generator import PatternGrid
from skiddie.utils import Screen, MultiScreenApp


class PatternScreen(Screen):
    """The screen used for displaying the challenge and prompting the user for a solution.

    Attributes:
        challenge_grid: The pattern grid to challenge the user with.
        solution_grids: The list of possible solutions that the user is prompted to select from.
    """
    def __init__(
            self, multi_screen: MultiScreenApp, challenge_grid: PatternGrid,
            solution_grids: List[PatternGrid]) -> None:
        self.challenge_grid = challenge_grid
        self.solution_grids = solution_grids
        super().__init__(multi_screen)

    def get_root_container(self):
        solution_containers = [
            HSplit([
                self._get_grid_container(grid),
                # Button("Select", handler=lambda: self.multi_screen.app.exit(result=grid)),
                Button("Select", functools.partial(self.multi_screen.exit, result=grid)),
            ])
            for grid in self.solution_grids
        ]

        return FloatContainer(
            Box(
                Frame(
                    HSplit([
                            Box(self._get_grid_container(self.challenge_grid)),
                            VSplit(
                                solution_containers,
                                padding=2,
                            ),
                        ],
                        padding=1,
                    ),
                ),
            ),
            floats=[],
        )

    @staticmethod
    def _get_grid_container(pattern_grid: PatternGrid):
        """Get a container for a given pattern grid."""
        return Frame(
            Box(
                Label(
                    text=pattern_grid.format_grid,
                    dont_extend_width=True,
                ),
                padding_left=1,
                padding_right=1,
            ),
        )


class GameInterface(MultiScreenApp):
    """The UI for playing the game."""
    def __init__(self, challenge_grid: PatternGrid, solution_grids: List[PatternGrid]) -> None:
        self._pattern_screen = PatternScreen(self, challenge_grid, solution_grids)
        self._global_keybindings = self._create_global_keybindings()

        layout = Layout(container=self._pattern_screen.get_root_container())

        app = Application(layout, style=GUI_STYLE, key_bindings=self._global_keybindings)

        super().__init__(app, self._pattern_screen)

    @staticmethod
    def _create_global_keybindings() -> KeyBindings:
        bindings = KeyBindings()

        bindings.add("c-c")(lambda event: event.app.exit(exception=KeyboardInterrupt))
        bindings.add("tab")(focus_next)
        bindings.add("right")(focus_next)
        bindings.add("s-tab")(focus_previous)
        bindings.add("left")(focus_previous)

        return bindings
