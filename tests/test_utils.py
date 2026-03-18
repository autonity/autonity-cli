"""
Test util functions
"""

from datetime import datetime, timezone

import pytest
from click import ClickException
from web3 import Web3

from autonity_cli.constants import AutonDenoms
from autonity_cli.utils import (
    geth_keyfile_name,
    parse_commission_rate,
    parse_token_value_representation,
    parse_wei_representation,
)


def test_wei_parser() -> None:
    """Test Wei parser."""
    assert parse_wei_representation("1kwei") == AutonDenoms.KWEI_VALUE_IN_WEI
    assert parse_wei_representation("1mwei") == AutonDenoms.MWEI_VALUE_IN_WEI
    assert parse_wei_representation("1gwei") == AutonDenoms.GWEI_VALUE_IN_WEI
    assert parse_wei_representation("1szabo") == AutonDenoms.SZABO_VALUE_IN_WEI
    assert parse_wei_representation("1finney") == AutonDenoms.FINNEY_VALUE_IN_WEI
    assert parse_wei_representation("1auton") == AutonDenoms.AUTON_VALUE_IN_WEI
    assert parse_wei_representation("1aut") == AutonDenoms.AUTON_VALUE_IN_WEI

    # Fractional parts
    assert parse_wei_representation("0.2kwei") == 200
    assert parse_wei_representation("0.5auton") == AutonDenoms.FINNEY_VALUE_IN_WEI * 500
    assert parse_wei_representation("0.2") == AutonDenoms.FINNEY_VALUE_IN_WEI * 200


def test_token_value_parser() -> None:
    """Test token value parser."""
    assert parse_token_value_representation("3.12345", 5) == 312345
    assert parse_token_value_representation("3.12345", 4) == 31234
    assert parse_token_value_representation("3.12345", 3) == 3123
    assert parse_token_value_representation("3.12345", 2) == 312
    assert parse_token_value_representation("3.12345", 1) == 31
    assert parse_token_value_representation("3.12345", 0) == 3


def test_parse_commission_rate() -> None:
    """Test parse_commission_rate."""
    assert parse_commission_rate("100") == 100
    assert parse_commission_rate("0.9") == 9000
    assert parse_commission_rate("90%") == 9000
    assert parse_commission_rate("0.03") == 300
    assert parse_commission_rate("0.0001") == 1

    with pytest.raises(ClickException):
        parse_commission_rate("1")
    with pytest.raises(ClickException):
        parse_commission_rate("1.0")
    with pytest.raises(ClickException):
        parse_commission_rate("100.01")


def test_geth_keyfile_name() -> None:
    """Test geth keyfile name generation."""
    key_time = datetime.strptime(
        "2022-02-07T17-19-56.517538", "%Y-%m-%dT%H-%M-%S.%f"
    ).replace(tzinfo=timezone.utc)

    key_address = Web3.to_checksum_address("ca57f3b40b42fcce3c37b8d18adbca5260ca72ec")

    assert geth_keyfile_name(key_time, key_address) == (
        "UTC--2022-02-07T17-19-56.517538000Z--"
        "ca57f3b40b42fcce3c37b8d18adbca5260ca72ec"
    )
