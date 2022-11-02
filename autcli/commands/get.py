"""
The aut get command group
"""

from autcli.utils import (
    to_json,
    validate_block_identifier,
    web3_from_endpoint_arg,
    newton_or_token_to_address,
)
from autcli.options import rpc_endpoint_option, newton_or_token_option
from autcli.user import get_account_stats, get_node_stats, get_block

from autonity.erc20 import ERC20

import sys
from web3 import Web3
from click import group, command, option, argument
from typing import List, Optional


@group()
def get() -> None:
    """
    Command group for getting blockchain information from the
    connected node.
    """


@command()
@rpc_endpoint_option
def stats(rpc_endpoint: Optional[str]) -> None:
    """
    Print general stats about RPC node and the blockchain it's on.
    """
    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    node_stats = get_node_stats(w3)
    print(to_json(node_stats))


@command()
@rpc_endpoint_option
@argument("identifier", default="latest")
def block(rpc_endpoint: Optional[str], identifier: str) -> None:
    """
    print information for block, where <identifier> is a block number or hash.
    """
    block_id = validate_block_identifier(identifier)
    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    block_data = get_block(w3, block_id)
    print(to_json(block_data))


@command()
@rpc_endpoint_option
@option(
    "--asof",
    help="state as of TAG, one of block number, 'latest', 'earliest', or 'pending'.",
)
@option(
    "--stdin",
    "use_stdin",
    is_flag=True,
    help="read account lines from stdin instead of positional arguments",
)
@argument("accounts", nargs=-1)
def account(
    rpc_endpoint: Optional[str],
    accounts: List[str],
    asof: Optional[str],
    use_stdin: bool,
) -> None:
    """
    print account tx count and balance state of one or more accounts.
    """

    if use_stdin:
        accounts = sys.stdin.read().splitlines()

    if len(accounts) == 0:
        print("No accounts specified")
        return

    addresses = [Web3.toChecksumAddress(act) for act in accounts]

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    account_stats = get_account_stats(w3, addresses, asof)

    for acct, act_stats in account_stats.items():
        print(f"{acct} {act_stats[0]} {act_stats[1]}")


@command()
@rpc_endpoint_option
@newton_or_token_option
@argument("account_str", metavar="ACCOUNT", nargs=1)
def balance(
    rpc_endpoint: Optional[str], account_str: str, ntn: bool, token: Optional[str]
) -> None:
    """
    Print the current balance of the given account.
    """
    account_addr = Web3.toChecksumAddress(account_str)
    token_addresss = newton_or_token_to_address(ntn, token)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)

    # TODO: support printing in other denominations (AUT / units based
    # on num decimals of token).

    if token_addresss is not None:
        token_contract = ERC20(w3, token_addresss)
        print(token_contract.balance_of(account_addr))

    else:
        print(w3.eth.get_balance(account_addr))


get.add_command(stats)
get.add_command(block)
get.add_command(account)
get.add_command(balance)
