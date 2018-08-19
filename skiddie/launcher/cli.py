"""The CLI for the game launcher.

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
import click

from prompt_toolkit import print_formatted_text

from skiddie.utils.ui import format_duration
from skiddie.launcher import gui
from skiddie.launcher.common import Game, GameSession, GAMES, Difficulty
from skiddie.launcher.scores import process_result, Scores, format_scores


def _get_game(name: str) -> Game:
    """Get a game from its name."""
    try:
        return [item for item in GAMES if item.game_name == name][0]
    except IndexError:
        raise click.BadParameter("'{0}'".format(name))


def _get_difficulty(name: str) -> Difficulty:
    """Get a difficulty from its name."""
    selected_difficulty = Difficulty.from_value(name)
    if not selected_difficulty:
        raise click.BadParameter("'{0}'".format(name))
    return selected_difficulty


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Run without any arguments to launch the GUI."""
    # If the command is run without any arguments, options or subcommands, run the GUI launcher.
    if ctx.invoked_subcommand is None:
        gui.main()


@cli.command(short_help="Play a game.")
@click.argument("game", type=str)
@click.option(
    "--difficulty", "-d", default="normal", show_default=True,
    help="The difficulty to play the game on. Accepted values are \"easy\", \"normal\" and \"hard\"."
)
def play(game: str, difficulty: str):
    """Play the game named GAME."""
    session = GameSession(_get_game(game), _get_difficulty(difficulty))
    session.play()
    process_result(session)


@cli.command(short_help="Get the description of a game.")
@click.argument("game", type=str)
def description(game: str):
    """Get the description of the game named GAME."""
    print(_get_game(game).description)


@cli.command(short_help="Get the high scores of a game.")
@click.argument("game", type=str)
@click.option(
    "--difficulty", "-d", default="normal", show_default=True,
    help="The difficulty to play the game on. Accepted values are \"easy\", \"normal\" and \"hard\"."
)
@click.option("--number", "-n", default=10, show_default=True, help="The number of high scores to show.")
def scores(game, difficulty, number):
    """Get the high scores of the game named GAME."""
    score_store = Scores()
    score_store.read()
    high_scores = score_store.get_scores(_get_game(game), _get_difficulty(difficulty))[:number]

    if not high_scores:
        return

    print_formatted_text(format_scores(high_scores))
