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

if os.name == "posix":
    CONFIG_DIR = os.path.join(os.getenv("XDG_CONFIG_HOME", os.path.join(os.getenv("HOME"), ".config")), "skiddie")
elif os.name == "nt":
    CONFIG_DIR = os.path.join(os.getenv("APPDATA"), "skiddie")
else:
    raise NotImplementedError("unsupported platform")

SCORES_FILE = os.path.join(CONFIG_DIR, "scores.json")

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
