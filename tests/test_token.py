from autonity_cli.commands.token import token_group

from autonity import Autonity, LiquidLogic
from eth_account import Account
from eth_typing import ChecksumAddress
from web3 import Web3


def _get_lntn_address(w3: Web3) -> ChecksumAddress:
    autonity = Autonity(w3)
    validator_address = autonity.get_validators()[0]
    validator = autonity.get_validator(validator_address)
    return validator.liquid_state_contract


def test_token_name(runner, w3):
    lntn_address = _get_lntn_address(w3)
    result = runner.invoke(token_group, ["name", "--token", lntn_address])
    assert result.exit_code == 0
    assert result.output == "LNTN-0\n"


def test_token_symbol(runner, w3):
    lntn_address = _get_lntn_address(w3)
    result = runner.invoke(token_group, ["symbol", "--token", lntn_address])
    assert result.exit_code == 0
    assert result.output == "LNTN-0\n"


def test_token_decimals(runner, w3):
    lntn_address = _get_lntn_address(w3)
    result = runner.invoke(token_group, ["decimals", "--token", lntn_address])
    assert result.exit_code == 0
    assert result.output == "18\n"


def test_token_total_supply(runner, w3):
    lntn_address = _get_lntn_address(w3)
    result = runner.invoke(token_group, ["total-supply", "--token", lntn_address])
    assert result.exit_code == 0
    assert result.output == "40000.000000000000000000\n"


def test_token_balance_of(runner, w3, treasury):
    lntn_address = _get_lntn_address(w3)
    result = runner.invoke(
        token_group, ["balance-of", "--token", lntn_address, treasury.address]
    )
    assert result.exit_code == 0
    assert result.output == "0.000000000000000000\n"


def test_token_allowance(runner, w3, treasury):
    lntn_address = _get_lntn_address(w3)
    result = runner.invoke(
        token_group, ["allowance", "--token", lntn_address, treasury.address]
    )
    assert result.exit_code == 0
    assert result.output == "0.000000000000000000\n"


def test_token_approval(runner, w3, treasury, user):
    lntn_address = _get_lntn_address(w3)
    lntn = LiquidLogic(w3, lntn_address)
    recipient = Account.create()
    start_balance = lntn.balance_of(treasury.address)

    approval_result = runner.invoke(
        token_group,
        [
            "approve",
            "--token",
            lntn_address,
            "--from",
            treasury.address,
            user.address,
            "10",
        ],
    )
    assert approval_result.exit_code == 0

    transfer_result = runner.invoke(
        token_group,
        [
            "transfer-from",
            "--token",
            lntn_address,
            "--from",
            user.address,
            treasury.address,
            recipient.address,
            "10",
        ],
    )
    assert transfer_result.exit_code == 0

    assert lntn.balance_of(recipient.address) == 10 * 10**18
    assert lntn.balance_of(treasury.address) == start_balance - 10 * 10**18
