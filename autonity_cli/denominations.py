"""
Utilities related to formatting token and Auton balances.
Constants related to known token precisions.
"""

from decimal import Decimal

AUTON_DECIMALS = 18
NEWTON_DECIMALS = 18


def format_quantity(units: int, decimals: int) -> str:
    """
    Given some quantity of atomic "token units" of a currency
    (e.g. Attoton for Auton), and the decimals used to represent the
    value of such a unit, return a string representation of the number
    of tokens.
    """
    adjusted = Decimal(units) * pow(Decimal(10), -decimals)
    return f"{adjusted:f}"


def format_auton_quantity(units: int) -> str:
    """
    Format a quantity of Wei as a string representing a quantity of
    Auton, with decimal places.
    """
    return format_quantity(units, AUTON_DECIMALS)


def format_newton_quantity(units: int) -> str:
    """
    Format a quantity of Newton units as a string representing a
    quantity of whole Newton, with decimal places.
    """
    return format_quantity(units, NEWTON_DECIMALS)
