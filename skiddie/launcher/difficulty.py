"""Classes for retrieving difficulty presets.

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
import json
from typing import Dict, Any

import pkg_resources

from skiddie.constants import DIFFICULTY_FILE, DIFFICULTY_TEMPLATE, JSON_INDENT
from skiddie.utils.misc import LateInit, recursive_update


class DifficultyPresets:
    """Persistent storage of difficulty presets."""
    def __init__(self) -> None:
        self._config_path = DIFFICULTY_FILE
        self._template_path = DIFFICULTY_TEMPLATE
        self._data = LateInit("cannot access data before the `read` method is called")

    def read(self) -> None:
        """Read the difficulty presets from storage, getting missing values from the template file."""
        with pkg_resources.resource_stream("skiddie", self._template_path) as template_file:
            template_data = json.load(template_file)

        try:
            with open(self._config_path, "r") as config_file:
                config_data = json.load(config_file)
        except FileNotFoundError:
            # The config file has not been created yet.
            config_data = {}

        self._data = recursive_update(template_data, config_data)

    def _get_game(self, game_name: str) -> Dict[str, Any]:
        """Get the data associated with a game."""
        try:
            return self._data[game_name]
        except IndexError:
            raise ValueError("The game '{0}' was not found".format(game_name))

    def get_difficulty(self, game_name: str, difficulty_name: str) -> Dict[str, Any]:
        """Get a dict of arguments for a given game and difficulty."""
        try:
            return self._get_game(game_name)["difficulties"][difficulty_name]
        except IndexError:
            raise ValueError("The difficulty '{0}' was not found".format(difficulty_name))

    def get_descriptions(self, game_name: str) -> Dict[str, str]:
        """Get a dict of argument names and descriptions for a given game."""
        return self._get_game(game_name)["descriptions"]

    def write(self) -> None:
        """Write the difficulty presets to storage.

        It is necessary to write to storage even if the difficulty presets have not been modified because new data may
        have been added to the template. This data needs to be written to the user's config file.
        """
        with open(self._config_path, "w") as config_file:
            json.dump(self._data, config_file, indent=JSON_INDENT, sort_keys=True)
