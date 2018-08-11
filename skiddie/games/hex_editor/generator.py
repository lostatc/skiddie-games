"""Code for generating a random maze.

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
import re
import random
import itertools
from typing import List, NamedTuple

from prompt_toolkit.formatted_text import FormattedText

# All the valid characters that can be used for each tile.
VALID_TILE_CHARS = "0123456789abcdef"

# The number of characters to be used for each tile.
CHARS_PER_TILE = 2

# The string that separates each row in the formatted grid string.
GRID_ROW_SEPARATOR = "\n\n"

# The string that separates each column in the formatted grid string.
GRID_COLUMN_SEPARATOR = "  "

# The regex pattern used to match the x and y coordinates in a string.
COORDINATE_PATTERN = "^\s*\(?\s*([0-9]+)\s*,\s*([0-9]+)\s*\)?\s*$"

# A pair of x and y coordinates.
Coordinates = NamedTuple("Coordinates", [("x", int), ("y", int)])


class MazeTile:
    """A tile in a grid of tiles that form a maze.

    Attributes:
        label: The text that is displayed to represent the tile in the maze.
        coordinates: The x and y coordinates of the tile in the grid.
    """
    def __init__(self, label: str, coordinates: Coordinates):
        self.label = label
        self.coordinates = coordinates
        self.visited = False

    def visit(self) -> None:
        """Visit the tile."""
        self.visited = True

    def check_valid_label(self, other: "MazeTile") -> bool:
        """Return whether the other maze tile has a label which allows them to connect.

        Returns:
            True if the two labels share at least one character and False otherwise.
        """
        for char in self.label:
            if char in other.label:
                return True

        return False

    @classmethod
    def create_random(cls, coordinates: Coordinates) -> "MazeTile":
        """Create a new instance with a random label."""
        random_label = "".join(random.choice(VALID_TILE_CHARS) for _ in range(CHARS_PER_TILE))
        return cls(random_label, coordinates)

    @classmethod
    def from_existing(cls, tile: "MazeTile", coordinates: Coordinates) -> "MazeTile":
        """Create a new instance whose label shares at least one character with the given one."""
        matching_char = random.choice(tile.label)
        random_chars = [random.choice(VALID_TILE_CHARS) for _ in range(CHARS_PER_TILE - len(matching_char))]
        new_label = [matching_char, *random_chars]
        random.shuffle(new_label)
        return cls("".join(new_label), coordinates)


class MazeGrid:
    """A grid of tiles that form a maze.

    Attributes:
        grid: A list of rows, each of which is a list of columns.
    """
    def __init__(self, grid: List[List[MazeTile]]):
        self.grid = grid

    @property
    def width(self) -> int:
        """The number of columns in the grid."""
        return len(max(self.grid, key=len))

    @property
    def height(self) -> int:
        """The number of rows in the grid."""
        return len(self.grid)

    def get_from_coordinates(self, coordinates: Coordinates) -> MazeTile:
        """Return a maze tile from the given coordinates.

        Raises:
            ValueError: The given coordinate are invalid.
        """
        x, y = coordinates

        if x < 0 or y < 0:
            raise ValueError("The given coordinates must not be negative")

        try:
            return self.grid[y][x]
        except IndexError:
            raise ValueError("The given coordinates are out of bounds")

    def get_from_user_coordinates(self, coordinates: Coordinates) -> MazeTile:
        """Return a maze tile from the given coordinates as displayed to the user.

        For this method, the origin is at the lower left corner of the grid. This is to account for how the coordinates
        are displayed to the user.

        Raises:
            ValueError: The given coordinate are invalid.
        """
        x, y = coordinates

        return self.get_from_coordinates(Coordinates(x, self.height - (y+1)))

    def get_from_user_string(self, coordinate_string: str) -> MazeTile:
        """Return a maze tile based on the given coordinates as displayed to the user.

        For this method, the origin is at the lower left corner of the grid. This is to account for how the coordinates
        are displayed to the user.

        Args:
            coordinate_string: A string containing the coordinates.

        Raises:
            ValueError: The given coordinate string is invalid.
        """
        coordinate_regex = re.compile(COORDINATE_PATTERN)
        match = coordinate_regex.search(coordinate_string)

        if not match:
            raise ValueError("Invalid syntax for coordinate string")

        coordinates = Coordinates(int(match.group(1)), int(match.group(2)))
        return self.get_from_user_coordinates(coordinates)

    def _get_adjacent(self, coordinates: Coordinates) -> List[MazeTile]:
        """Return the tiles adjacent to the tile at the given coordinates."""
        x, y = coordinates
        output = []

        for x_offset, y_offset in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            adjacent_x = x + x_offset
            adjacent_y = y + y_offset

            if adjacent_x < 0 or adjacent_y < 0:
                continue

            try:
                output.append(self.get_from_coordinates((adjacent_x, adjacent_y)))
            except ValueError:
                continue

        return output

    def check_visitable(self, tile: MazeTile) -> bool:
        """Return whether the tile at the given coordinates can be visited.

        Returns:
            True if there is an adjacent tile which shares at least on character with the given tile, and False
            otherwise.
        """
        for adjacent_tile in self._get_adjacent(tile.coordinates):
            if adjacent_tile.visited and tile.check_valid_label(adjacent_tile):
                return True

        return False

    def check_complete(self) -> bool:
        """Return whether the maze has been completed.

        Returns:
            True if there is a visited tile along the right edge of the grid, and False otherwise.
        """
        return any(row[-1].visited for row in self.grid)

    def format_grid(
            self, visited_style: str = "reverse", add_coords: bool = True,
            coords_style: str = "italic bold fg:ansibrightcyan") -> FormattedText:
        """Format the grid as a single string.

        Args:
            visited_style: The style string to apply to tiles which have been visited.
            add_coords: Show coordinates in the top and left edges of the screen.
            coords_style: The style string to apply to the coordinates.
        """
        style_pairs = []

        # This is the number of characters that are needed to display the row coordinates in the first column.
        coord_column_padding = len("{0:d}".format(self.height))

        for i, row in enumerate(self.grid):
            # Add the coordinate for this row.
            if add_coords:
                style_pairs.append((coords_style, "{0:{1}d}".format(self.height - (i+1), coord_column_padding)))
                style_pairs.append(("", GRID_COLUMN_SEPARATOR))

            for tile in row:
                # Add the tile.
                if tile.visited:
                    style_pairs.append((visited_style, tile.label))
                else:
                    style_pairs.append(("", tile.label))

                # Add the space between each tile.
                style_pairs.append(("", GRID_COLUMN_SEPARATOR))

            # Remove the trailing space.
            style_pairs.pop()

            # Add the newline between each row.
            style_pairs.append(("", GRID_ROW_SEPARATOR))

        # Add the coordinates on top edge.
        if add_coords:
            # Add whitespace to account for the space taken up by the coordinates on the left edge of the grid.
            style_pairs.append(("", " "*coord_column_padding))
            style_pairs.append(("", GRID_COLUMN_SEPARATOR))

            # Add the coordinates for each column.
            for number in range(self.width):
                style_pairs.append((coords_style, "{0:{1}d}".format(number, CHARS_PER_TILE)))
                style_pairs.append(("", GRID_COLUMN_SEPARATOR))

        return FormattedText(style_pairs)

    @classmethod
    def create_random(
            cls, width: int, height: int, forward_weight: int, sideways_weight: int,
            min_distance: int, max_distance: int) -> "MazeGrid":
        """Create a new random grid with at least one valid path connecting both sides.

        Args:
            width: The number of columns in the grid.
            height: The number of rows in the grid.
            forward_weight: The relative weight given to forward moves when generating the path.
            sideways_weight: The relative weight given to sideways moves when generating the path.
            min_distance: The minimum length for a segment of the generated path through the maze grid.
            max_distance: The maximum length for a segment of the generated path through the maze grid.
        """
        # Generate a completely random grid.
        grid = [
            [MazeTile.create_random(Coordinates(x, y)) for x in range(width)]
            for y in range(height)
        ]
        maze_grid = cls(grid)

        # Pick a random starting point on the left edge and create a tile there.
        start_coordinates = Coordinates(0, random.choice(range(height)))
        start_tile = MazeTile.create_random(start_coordinates)

        # Add the tile to the grid.
        maze_grid.grid[start_coordinates.y][start_coordinates.x] = start_tile
        start_tile.visit()

        # This list contains the coordinate offsets for moving in each direction. Each offset appears in here multiple
        # times, with the relative number of times corresponding to the likelihood that it will be picked.
        weighted_offsets = (
            [Coordinates(1, 0)] * forward_weight
            + [Coordinates(0, 1)] * sideways_weight
            + [Coordinates(0, -1)] * sideways_weight
        )

        current_coordinates = start_coordinates
        previous_tile = start_tile

        # This is a set of all the coordinates that have been used in the path so far.
        used_coordinates = {start_coordinates}

        # Until the path reaches the right edge, walk a random distance in a random direction.
        while not any(coordinates.x == (width - 1) for coordinates in used_coordinates):
            offset_coordinates = random.choice(weighted_offsets)
            walk_distance = random.randint(min_distance, max_distance)

            # Get the coordinates at the end of this walk.
            end_coordinates = Coordinates(
                current_coordinates.x + (offset_coordinates.x * walk_distance),
                current_coordinates.y + (offset_coordinates.y * walk_distance),
            )

            # Get all the coordinates between the current tile and the end tile. Make sure both ranges are at least the
            # same length so that they can be iterated over together.
            def get_range(start, end):
                if start == end:
                    return itertools.repeat(start)
                elif end < start:
                    return range(start-1, end-1, -1)
                else:
                    return range(start+1, end+1)

            x_range = get_range(current_coordinates.x, end_coordinates.x)
            y_range = get_range(current_coordinates.y, end_coordinates.y)

            # These are all the coordinates between the current tile and the end tile.
            walk_coordinates = [Coordinates(x, y) for x, y in zip(x_range, y_range)]

            # Create the tiles at these coordinates.
            for coordinate_pair in walk_coordinates:
                # Check if the coordinates are out of bounds.
                try:
                    maze_grid.get_from_coordinates(coordinate_pair)
                except ValueError:
                    break

                # Check if the path intersects itself.
                if coordinate_pair in used_coordinates:
                    break

                # Create the new tile.
                new_tile = MazeTile.from_existing(previous_tile, coordinate_pair)

                # Add the new tile to the grid.
                maze_grid.grid[coordinate_pair.y][coordinate_pair.x] = new_tile
                used_coordinates.add(coordinate_pair)

                previous_tile = new_tile
                current_coordinates = coordinate_pair

        return maze_grid
