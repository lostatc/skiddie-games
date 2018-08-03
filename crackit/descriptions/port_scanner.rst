A game about scanning network ports.

The game starts with five numbers on the screen in a row. Some combination of
addition and subtraction of the first four numbers yields the fifth number. You
can also think of it as some of the first four numbers being negative with the
sum yielding the fifth number. Examples::

    3.12.6.5:10  ->  - 3 + 12 + 6 - 5 = 10


Below these numbers is a second row of four numbers with the fifth one missing.
The objective of the game is to determine what the fifth number should be. To
find the fifth number, you need to determine what the rules of addition and
subtraction are for the upper row and apply them to the lower row. Example::

    7.10.6.2:5  ->  + 7 - 10 + 6 + 2 = 5
    1.5.11.3:   ->  + 1 - 5 + 11 + 3 = 10
