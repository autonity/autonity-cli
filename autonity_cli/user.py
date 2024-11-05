"""
'User' functions. These functions encapsulate the functionality of
the CLI commands and emulate their usage as much as makes
sense. Return values are python types, as the 'commands' functions
hand json translation.

If aut implements an ipyothon 'console mode', perhaps these are the
functions meant to be called in that.
"""

from typing import List, Optional, TypedDict

from autonity import Autonity
from web3 import Web3
from web3.types import (
    BlockData,
    BlockIdentifier,
    ChecksumAddress,
)

from .denominations import (
    format_auton_quantity,
    format_newton_quantity,
)


class AccountStats(TypedDict):
    """
    Dict holding information about a specific account.
    """

    account: ChecksumAddress
    tx_count: int
    balance: str
    ntn_balance: str


def get_account_stats(
    w3: Web3, accounts: List[ChecksumAddress], tag: Optional[BlockIdentifier] = None
) -> List[AccountStats]:
    """
    For a list of accounts, return a dictionary with accounts as keys
    and list of transaction count and balance (in that order) as
    values. Tag is one of None, 'latest', 'earliest', 'pending' or a
    block number, and the values are as of block described by the
    tag. The underlying RPC methods are eth_getBalance and
    eth_getTransactionCount.
    """
    stats: List[AccountStats] = []
    autonity = Autonity(w3)
    for acct in accounts:
        txcount = w3.eth.get_transaction_count(acct)
        if tag is None:
            balance = w3.eth.get_balance(acct)
        else:
            balance = w3.eth.get_balance(acct, tag)
        ntn_balance = autonity.balance_of(acct)
        stats.append(
            {
                "account": acct,
                "tx_count": txcount,
                "balance": format_auton_quantity(balance),
                "ntn_balance": format_newton_quantity(ntn_balance),
            }
        )

    return stats


# TODO: Properly typed object.
# TODO: Move to autonity.py
def get_block(w3: Web3, identifier: BlockIdentifier) -> BlockData:
    """
    Returns a dictionary of block data for the block identified by
    'identifier', which is either a block number/height or string
    representation of a 32 byte block hash.
    """
    block_data = w3.eth.get_block(identifier)
    return block_data
