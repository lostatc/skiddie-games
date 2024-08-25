A game about editing binary data.

The game starts with a grid of tiles on the screen, with each tile containing
two characters. On the left and bottom edges of the grid are coordinate axes.
The objective is to form a path between the left and right edges of the grid by
visiting the tiles in between. You can visit a tile by typing in its
coordinates, but only if is is adjacent to another visited tile that shares at
least one character in common with it. Example:

    2  c9  ff  de

    1  9b  b3  b1

    0  61  2b  aa

        0   1   2

From tile (0, 1), you can visit either tile (1, 1) or tile (0, 2). From tile
(1, 1), you can only visit tile (2, 1)
