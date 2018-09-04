A game about building trees from a closure table.

The game starts with an empty tree on the left side of the screen and a table
of values of the right. The objective of the game is to fill in the values of
the tree from the information in the table. Each row in the table represents a
relationship between two nodes in the tree. The node in the first column is an
ancestor of the node in the second column. It could be a parent, grandparent,
great-grandparent and so on. The value in the third column is the number of
levels between the two nodes. Using this information, it's possible to figure
out where each node is in the tree. Example:

    Hamburg         Ancestor  Descendant  Distance
    ├─Hanover       Hamburg   Hamburg     0
    │ └─Berlin      Hamburg   Hanover     1
    └─Munich        Hamburg   Munich      1
                    Hamburg   Berlin      2
                    Hanover   Hanover     0
                    Hanover   Berlin      1
                    Berlin    Berlin      0
                    Munich    Munich      0

To fill in a value, type it in. To move the cursor between different positions
in the tree, use the `Tab` or arrow keys. Once each value in the tree is
filled, move the cursor to the "Done" button and press `Enter`.
