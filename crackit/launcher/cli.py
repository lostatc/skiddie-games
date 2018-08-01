"""The CLI for the game launcher.

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
import click
from prompt_toolkit import print_formatted_text

from crackit.launcher import gui
from crackit.launcher.common import Game, GAMES, Difficulty


def _get_game(name: str) -> Game:
    """Get a game from its name."""
    try:
        return [item for item in GAMES if item.name == name][0]
    except IndexError:
        raise click.BadParameter("'{0}'".format(name))


def _get_difficulty(name: str) -> Difficulty:
    """Get a difficulty from its name."""
    try:
        return [item for item in Difficulty if item.value.lower() == name.lower()][0]
    except IndexError:
        raise click.BadParameter("'{0}'".format(name))


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    # If the command is run without any arguments, options or subcommands, run the GUI launcher.
    if ctx.invoked_subcommand is None:
        gui.main()


@cli.command(name="play", short_help="Play a game.")
@click.argument("game", type=str)
@click.option(
    "--difficulty", "-d", default="normal",
    help="The difficulty to play the game on. Accepted values are \"easy\", \"normal\" and \"hard\"."
)
def play(game: str, difficulty: str):
    """Play the game named GAME."""
    _get_game(game).launcher(_get_difficulty(difficulty))


@cli.command(name="get-description", short_help="Get the description of a game.")
@click.argument("game", type=str)
def get_description(game: str):
    """Get the description of the game named GAME."""
    print_formatted_text(_get_game(game).description)
