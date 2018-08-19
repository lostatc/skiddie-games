"""Functions related to numbers, ranges and iteration.

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
import itertools
import random
import math
from typing import Sequence, Iterator, List, TypeVar, Union

T = TypeVar("T")


def get_random_cycle(sequence: Sequence[T]) -> Iterator[T]:
    """Return a randomized cycle of the given sequence."""
    random_sequence = list(sequence)
    random.shuffle(random_sequence)
    return itertools.cycle(random_sequence)


def take_random_cycle(sequence: Sequence[T], items: int) -> List[T]:
    """Take a given number of elements from a random cycle."""
    random_cycle = get_random_cycle(sequence)
    return [next(random_cycle) for _ in range(items)]


def sample_and_sort(sequence: Sequence[T], num_items: int) -> Sequence[T]:
    """Randomly sample a given number of integers from the given sequence and sort them."""
    return sorted(random.sample(sequence, num_items))


def limit_range(min_value: int, max_value: int, range_size: int) -> Sequence[int]:
    """Choose a random range between the minimum and maximum given values.

    Args:
        min_value: The minimum value for the start for the range to be selected.
        max_value: The maximum value for the end for the range to be selected.
        range_size: The maximum size for the range to be selected.

    Returns:
        A range of integers.
    """
    start = random.randrange(min_value, max_value - range_size)
    end = start + range_size
    return range(start, end)


def sample_decimal_range(min_value: int, max_value: int, num_items: int, decimal_places: int = 2) -> Sequence[float]:
    """Sample from a range of decimal numbers between the given minimum and maximum values."""
    multiple = 10**decimal_places
    int_values = sample_and_sort(range(min_value * multiple, max_value * multiple), num_items)
    float_values = [integer / multiple for integer in int_values]
    return float_values


def sample_partitions(
        min_value: int, max_value: int, num_items: int, decimal_places: int = 2,
        partition_magnitude=1) -> Sequence[Union[float, int]]:
    """Take samples equally split between multiple unequally-sized partitions.

    Args:
        min_value: The minimum value for numbers to be selected.
        max_value: The maximum value for numbers to be selected.
        num_items: The number of items to select.
        decimal_places: The number of decimal places that the returned numbers will have. If this is 0, then return
            ints.
        partition_magnitude: The size of each partition as a number of orders of magnitude.

    """
    ranges = []
    start_exponent = math.floor(math.log10(min_value))
    stop_exponent = math.floor(math.log10(max_value))

    # Get the range of numbers in each order of magnitude.
    for exponent in itertools.count(start_exponent, step=partition_magnitude):
        next_exponent = exponent + partition_magnitude
        start = 10**exponent
        stop = max_value if next_exponent == stop_exponent else 10**next_exponent

        ranges.append(range(start, stop))

        if stop >= max_value:
            break

    # Figure out how many numbers to sample from each range.
    min_sample_size, remainder = divmod(num_items, len(ranges))
    sample_sizes = [min_sample_size] * len(ranges)
    for i in range(remainder):
        sample_sizes[i] += 1
    random.shuffle(sample_sizes)

    output = []

    # Take a sample in each range.
    for sample_range, sample_size in zip(ranges, sample_sizes):
        output += sample_decimal_range(
            sample_range[0], sample_range[-1], sample_size, decimal_places=decimal_places
        )

    if decimal_places == 0:
        output = [round(number) for number in output]

    return output
