"""A game about scanning network ports.

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
import random
from typing import List, Tuple

from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator, ValidationError

from skiddie.utils import LateInit, print_banner

# The number of sections in the IP address.
ADDRESS_SECTIONS = 4

# The minimum possible port number.
MIN_PORT = 1

# The maximum possible port number.
MAX_PORT = 49151

# The string that separates sections of the IP address.
SECTION_SEPARATOR = "."

# The string that separates the IP address from the port.
PORT_SEPARATOR = ":"

# A list of tuples of string templates. The first value in each tuple is a valid Linux command that can be used to scan
# ports, and the second is a list of realistic outputs from that command.
SCAN_COMMAND_TEMPLATES = [(
        "$ netcat -zv {ip} {port}", [
            "Connection to {ip} {port} port [{protocol}] succeeded!",
            "nc: connect to {ip} port {port} ({protocol}) failed: Network is unreachable",
        ]
    ),
]

# A list of common protocol names.
PROTOCOLS = [
    "tcp/echo", "udp/echo", "tcp/netstat", "tcp/ftp", "tcp/ssh", "tcp/telenet", "tcp/smtp", "tcp/time", "udp/time",
    "tcp/whois", "tcp/http", "tcp/pop3", "tcp/sftp", "tcp/ntp", "udp/ntp", "tcp/irc", "udp/irc", "tcp/ldap", "udp/ldap",
    "tcp/https", "tcp/socks", "udp/socks", "tcp/openvpn", "udp/openvpn", "tcp/nfs", "udp/nfs", "tcp/mysql", "udp/mysql",
    "tcp/svn", "udp/svn", "tcp/http-alt", "udp/http-alt",
]


def print_filler(ip_address: str, port: str) -> None:
    """Print hacker-themed filler text to stdout.

    This prints a valid port-scanning command with realistic output.

    Args:
        ip_address: The ip address to include in the output.
        port: The port number to include in the output.
    """
    command_template, output_templates = random.choice(SCAN_COMMAND_TEMPLATES)
    command = command_template.format(ip=ip_address, port=port)
    output = random.choice(output_templates).format(
        ip=ip_address, port=port, protocol=random.choice(PROTOCOLS)
    )
    filler = "\n".join([command, output])

    print("\n{0}\n".format(filler))


class AddressChallenge:
    """A set of numbers that form a challenge for the user to solve.

    Attributes:
        sections: The list of numbers which each form a section of the IP address and sum to form the solution.
        max_section_number: The maximum possible positive number for each section.
    """
    max_section_number = LateInit()

    def __init__(self, sections: List[int]) -> None:
        self.sections = sections

    @property
    def solution(self) -> int:
        """The solution to the challenge."""
        return sum(self.sections)

    def format_address(self, use_abs=True) -> str:
        """Format the challenge as an IPV4 address.

        Args:
            use_abs: Make the numbers in each section positive, obscuring the solution.

        Returns:
            The formatted address.
        """
        return SECTION_SEPARATOR.join(
            str(abs(number)) if use_abs else str(number)
            for number in self.sections
        )

    def format_port(self) -> str:
        """Format the challenge as a port number.

        Returns:
            The formatted address.
        """
        return str(self.solution)

    def format_socket(self, include_solution: bool = True, use_abs=True) -> str:
        """Format the challenge as an IPV4 address with a port.

        Args:
            include_solution: Include the solution in the formatted string.
            use_abs: Make the numbers in each section positive, obscuring the solution.

        Returns:
            The formatted socket.
        """
        return "{0}{1}{2}".format(
            self.format_address(use_abs),
            PORT_SEPARATOR,
            str(self.solution) if include_solution else ""
        )

    @classmethod
    def create_random(cls, template=None):
        """Create a new random challenge.

        This will always generate a challenge with a positive solution.

        Args:
            template: An AddressChallenge instance. If provided, then the generated instance will have positive and
                negative numbers in the same places as the template. If None, positive and negative numbers are decided
                randomly.

        Returns:
            A new AddressChallenge instance.
        """
        # Decide which sections should be positive and negative. This is a list of positive and negative integers
        # representing the signs of each section.
        if not template:
            # Randomly decide which sections should be positive and negative. No more than half of these sections can be
            # negative for the solution to be positive.
            max_negative_sections = ADDRESS_SECTIONS // 2
            negative_sections = [-1 for _ in range(random.randint(0, max_negative_sections))]
            positive_sections = [1 for _ in range(ADDRESS_SECTIONS - len(negative_sections))]
            template_signs = [*negative_sections, *positive_sections]
            random.shuffle(template_signs)
        else:
            # Use the provided template to decide which sections should be positive and negative.
            template_signs = template.sections

        # Ensure that the generated number has the same sign as the corresponding template section and that it is
        # within the bounds of possible numbers.
        def get_constraints(sign: int) -> Tuple[int, int]:
            """Get the minimum and maximum possible values for a section with a given sign."""
            return (-cls.max_section_number, -1) if sign < 0 else (0, cls.max_section_number)

        def constrain(number: int, sign: int) -> int:
            """Ensure that the number is within the constraints."""
            min_constraint, max_constraint = get_constraints(sign)

            if number > max_constraint:
                return max_constraint
            if number < min_constraint:
                return min_constraint
            return number

        # Randomly generate the sections of the challenge.
        sections = []
        for i, current_sign in enumerate(template_signs):
            running_sum = sum(sections)
            remaining_signs = template_signs[i+1:]

            # Get the maximum and minimum possible sums of the sections. These are the sums you would get if you made
            # all the remaining sections their highest or lowest possible values.
            max_possible_sum = running_sum + sum(get_constraints(sign)[1] for sign in remaining_signs)
            min_possible_sum = running_sum + sum(get_constraints(sign)[0] for sign in remaining_signs)

            # Get the upper and lower bound for the next section.
            lower_bound = constrain(MIN_PORT - max_possible_sum, current_sign)
            upper_bound = constrain(MAX_PORT - min_possible_sum, current_sign)

            section = random.randrange(lower_bound, upper_bound)
            sections.append(section)

        return cls(sections)


class SolutionValidator(Validator):
    """A validator which ensures that the provided solution is a digit which solves the puzzle."""
    def __init__(self, solution: int) -> None:
        self.solution = solution

    def validate(self, document) -> None:
        text = document.text

        if not text.isdecimal():
            raise ValidationError(message="Must be a number", cursor_position=len(text))

        if int(text) != self.solution:
            raise ValidationError(message="Wrong port number", cursor_position=len(text))


def play(challenges_to_win: int, number_of_examples: int, max_section_number: int) -> None:
    """Play the game.

    Args:
        number_of_examples: The number of completed IP addresses that come before each challenge.
        challenges_to_win: The number of challenges that must be completed to win the game.
        max_section_number: The maximum possible number for each section of the IP address.
    """
    AddressChallenge.max_section_number = max_section_number

    session = PromptSession(validate_while_typing=False, mouse_support=True)

    for _ in range(challenges_to_win):
        example = AddressChallenge.create_random()
        challenge = AddressChallenge.create_random(template=example)

        # Print examples.
        for _ in range(number_of_examples):
            example_copy = AddressChallenge.create_random(template=example)
            print(example_copy.format_socket(include_solution=True))

        # Prompt for the challenge.
        session.prompt(
            challenge.format_socket(include_solution=False),
            validator=SolutionValidator(challenge.solution)
        )

        print_filler(challenge.format_address(), challenge.format_port())

    print_banner("ACCESS GRANTED", style="ansigreen bold")
