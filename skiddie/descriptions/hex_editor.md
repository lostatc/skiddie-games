A game about editing binary data.

The game starts with a grid of tiles on the screen, with each tile containing
two characters. On the left and bottom edges of the grid are coordinate axes.
The objective is to form a path between the left and right edges of the grid by
visiting the tiles in between. You can visit a tile by typing in its
coordinates, but only if is is adjacent to another visited tile that shares at
least one character in common with it. Example:

    1c  ff

    9b  b3

    61  2b

If the tile `9b` has been visited, then the only tile which it can visit is
`b3`. This is because the two tiles are adjacent and have a character in
common. When the game starts, one tile on the left edge of the screen will have
been visited.
