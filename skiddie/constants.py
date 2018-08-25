"""Package-wide constants.

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
import os

from prompt_toolkit.styles import Style

# The path in which to put config files and persistent user data.
if os.name == "posix":
    CONFIG_DIR = os.path.join(os.getenv("XDG_CONFIG_HOME", os.path.join(os.getenv("HOME"), ".config")), "skiddie")
elif os.name == "nt":
    CONFIG_DIR = os.path.join(os.getenv("APPDATA"), "skiddie")
else:
    raise NotImplementedError("unsupported platform")

# The path of the file containing the user's scores.
SCORES_FILE = os.path.join(CONFIG_DIR, "scores.json")

# The path of the file containing the user's difficulty presets.
DIFFICULTY_FILE = os.path.join(CONFIG_DIR, "difficulty.json")

# The name of the directory containing descriptions of each game relative to the root package. Because this is a
# resource string and not a filesystem path, it must use forward slashes.
DESCRIPTIONS_DIR = "descriptions"

# The name of the directory containing template files relative to the root package. Because this is a resource string
# and not a filesystem path, it must use forward slashes.
TEMPLATES_DIR = "templates"

# The path of the template file containing the default difficulty presets. Because this is a resource string and not a
# filesystem path, it must use forward slashes.
DIFFICULTY_TEMPLATE = "/".join([TEMPLATES_DIR, "difficulty.json"])

# The master style sheet for all GUIs.
GUI_STYLE = Style([
    ("button.focused", "bg:ansired"),
    ("dialog.body", "fg:ansidefault bg:ansidefault"),
    ("dialog shadow", "fg:ansibrightblack bg:ansibrightblack"),
    ("dialog frame.label", "fg:ansigreen"),
    ("cursor-line", "fg:ansidefault bg:ansidefault reverse nounderline"),
    ("cursor-column", "fg:ansidefault bg:ansidefault reverse"),
    ("selectable-label", ""),
    ("selectable-label.focused", "reverse"),
    ("column-name", "bold"),
])
