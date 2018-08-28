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

from skiddie.constants import DEFAULT_DIFFICULTY
from skiddie.launcher import gui
from skiddie.exceptions import MissingConfigKeyError
from skiddie.launcher.games import Game, GameSession, GAMES
from skiddie.launcher.scores import process_result, Scores, format_scores, ScoreSort


def _get_game(name: str) -> Game:
    """Get a game from its name."""
    try:
        return next(item for item in GAMES if item.game_name.lower() == name.lower())
    except StopIteration:
        raise click.BadParameter("'{0}'".format(name))


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
    "--difficulty", "-d", default=DEFAULT_DIFFICULTY, show_default=True,
    help="The difficulty to play the game on."
)
def play(game: str, difficulty: str):
    """Play the game named GAME."""
    session = GameSession(_get_game(game), difficulty)

    try:
        session.play()
    except MissingConfigKeyError as error:
        raise click.BadParameter("'{0}'".format(error.key))

    process_result(session)


@cli.command(short_help="Get the description of a game.")
@click.argument("game", type=str)
def description(game: str):
    """Get the description of the game named GAME."""
    print(_get_game(game).description)


@cli.command(short_help="Get the high scores of a game.")
@click.argument("game", type=str)
@click.option(
    "--difficulty", "-d", default=DEFAULT_DIFFICULTY, show_default=True,
    help="The difficulty that the game was played on."
)
@click.option("--number", "-n", default=25, show_default=True, help="The number of high scores to show.")
@click.option("--sort-column", "-s", default="score", show_default=True, help="The column to sort the scores by.")
def scores(game, difficulty, number, sort_column):
    """Get the high scores of the game named GAME."""
    score_store = Scores()
    with score_store:
        try:
            high_scores = score_store.get_scores(_get_game(game), difficulty)[:number]
        except MissingConfigKeyError:
            raise click.BadParameter("'{0}'".format(difficulty))

    sort_method = ScoreSort.from_name(sort_column)
    if not sort_method:
        raise click.BadParameter("'{0}'".format(sort_column))

    print_formatted_text(format_scores(high_scores, sort_method=sort_method))
