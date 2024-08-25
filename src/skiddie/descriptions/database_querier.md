A game about querying database tables.

The game starts with a table of data on the left side of the screen. This table
consists of rows and columns. On the right side of the screen is a series of
rules. The objective of the game is to identify the row in the table that
fulfills all of these rules. Here is an example of each type of rule:

    quantity >= 29
        The row is greater than or equal to 29 in the "quantity" column.

    date <= 2018-08-17
        The row is less than or equal to 2018-08-17 in the "date" column.

    $37.42 <= price <= $102.99
        The row is between $37.42 and $102.99 in the "price" column (inclusive).

    enabled == true
        The row is equal to true in the "enabled" column.

    priority != high
        The row is not equal to high in the "priority" column.

For each column in the table, there is a rule that helps to narrow down which
row is the correct one. Only one row in the table will fulfill all of the given
rules. To choose a row, select it using the `Tab` or arrow keys and press
`Enter`.
