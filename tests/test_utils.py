"""
Test util functions
"""

from datetime import datetime, timezone

from web3 import Web3

from autonity_cli.constants import AutonDenoms
from autonity_cli.utils import (
    geth_keyfile_name,
    parse_commission_rate,
    parse_token_value_representation,
    parse_wei_representation,
)


def test_wei_parser():
    assert AutonDenoms.KWEI_VALUE_IN_WEI == parse_wei_representation("1kwei")
    assert AutonDenoms.MWEI_VALUE_IN_WEI == parse_wei_representation("1mwei")
    assert AutonDenoms.GWEI_VALUE_IN_WEI == parse_wei_representation("1gwei")
    assert AutonDenoms.SZABO_VALUE_IN_WEI == parse_wei_representation("1szabo")
    assert AutonDenoms.FINNEY_VALUE_IN_WEI == parse_wei_representation("1finney")
    assert AutonDenoms.AUTON_VALUE_IN_WEI == parse_wei_representation("1auton")
    assert AutonDenoms.AUTON_VALUE_IN_WEI == parse_wei_representation("1aut")

    # Fractional parts
    assert 200 == parse_wei_representation("0.2kwei")
    assert AutonDenoms.FINNEY_VALUE_IN_WEI * 500 == parse_wei_representation("0.5auton")
    assert AutonDenoms.FINNEY_VALUE_IN_WEI * 500 == parse_wei_representation("0.5auton")
    assert AutonDenoms.FINNEY_VALUE_IN_WEI * 200 == parse_wei_representation("0.2")


def test_token_value_parser():
    assert 312345 == parse_token_value_representation("3.12345", 5)
    assert 31234 == parse_token_value_representation("3.12345", 4)
    assert 3123 == parse_token_value_representation("3.12345", 3)
    assert 312 == parse_token_value_representation("3.12345", 2)
    assert 31 == parse_token_value_representation("3.12345", 1)
    assert 3 == parse_token_value_representation("3.12345", 0)


def test_parse_commission_rate():
    assert 100 == parse_commission_rate("100")
    assert 9000 == parse_commission_rate("0.9")
    assert 9000 == parse_commission_rate("90%")
    assert 300 == parse_commission_rate("0.03")
    assert 1 == parse_commission_rate("0.0001")


def test_geth_keyfile_name():
    # time = datetime.fromisoformat("2022-02-07T17:19:56.517538000Z")
    key_time = datetime.strptime(
        "2022-02-07T17-19-56.517538", "%Y-%m-%dT%H-%M-%S.%f"
    ).replace(tzinfo=timezone.utc)

    key_address = Web3.to_checksum_address(
        "ca57f3b40b42fcce3c37b8d18adbca5260ca72ec"
    )

    assert (
        "UTC--2022-02-07T17-19-56.517538000Z--ca57f3b40b42fcce3c37b8d18adbca5260ca72ec"
        == geth_keyfile_name(key_time, key_address)
    )
