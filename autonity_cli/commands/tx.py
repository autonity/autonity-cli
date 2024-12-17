"""
The `tx` command group.
"""

import asyncio
import json
from typing import Optional

from click import ClickException, Path, argument, command, group, option
from eth_account.datastructures import SignedTransaction
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3

from .account import signtx
from ..erc20 import ERC20
from ..logging import log
from ..options import (
    from_option,
    keyfile_option,
    newton_or_token_option,
    rpc_endpoint_option,
    tx_aux_options,
    tx_value_option,
)
from ..tx import send_tx, wait_for_tx
from ..utils import (
    create_contract_tx_from_args,
    create_tx_from_args,
    finalize_tx_from_args,
    from_address_from_argument_optional,
    load_from_file_or_stdin,
    newton_or_token_to_address,
    parse_token_value_representation,
    to_json,
    validate_32byte_hash_string,
    web3_from_endpoint_arg,
)

# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments


@group(name="tx")
def tx_group() -> None:
    """
    Commands for transaction creation and processing.
    """


# Re-use the `account signtx` command as `tx sign`
tx_group.add_command(signtx, name="sign")


@command()
@rpc_endpoint_option
@newton_or_token_option
@keyfile_option()
@from_option
@option("--to", "-t", "to_str", help="address to which the transaction is directed.")
@tx_value_option(required=True)
@tx_aux_options
@option(
    "--data", "-d", help="compiled contract code OR method signature and parameters."
)
@option(
    "--legacy",
    is_flag=True,
    help="if set, transaction type is 0x0 (pre-EIP1559), otherwise type is 0x2.",
)
def make(
    rpc_endpoint: Optional[str],
    ntn: bool,
    token: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    to_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    value: str,
    data: Optional[str],
    chain_id: Optional[int],
    legacy: bool,
) -> None:
    """
    Create a transaction from the parameters passed in.
    """

    # TODO: Add a flag which results in only unconnected Web3
    # instances being created.  Callers who do not want to connect to
    # a node will then receive an error if they do not specify all
    # required values (rather than having Web3.py silently connect).

    # Potentially used in multiple places, so avoid re-initializing.
    w3: Optional[Web3] = None

    # If from_str is not set, take the address from a keyfile instead
    # (if given)
    from_addr = from_address_from_argument_optional(from_str, keyfile)
    log(f"from_addr: {from_addr}")

    to_addr = Web3.to_checksum_address(to_str) if to_str else None

    if to_addr is None:
        raise ClickException(
            "`--to` address must be specified (contract deployment not yet supported)"
        )

    token_addresss = newton_or_token_to_address(ntn, token)

    # If --fee-factor was given, we must do some computation up-front

    # If this is a token call, fill in the "to" and "data" fields
    # using the contract call.  Otherwise, for a plain AUT transfer,
    # use create_transaction and finalize_transaction wrappers.

    if token_addresss:
        if not from_addr:
            raise ClickException("`--from` address not specified")

        w3 = web3_from_endpoint_arg(w3, rpc_endpoint)
        erc = ERC20(w3, token_addresss)
        token_units = parse_token_value_representation(value, erc.decimals())
        function = erc.transfer(to_addr, token_units)
        tx = create_contract_tx_from_args(
            function=function,
            from_addr=from_addr,
            gas=gas,
            gas_price=gas_price,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            fee_factor=fee_factor,
            nonce=nonce,
            chain_id=chain_id,
        )

    else:
        if not from_addr:
            raise ClickException("`--from` address not specified")

        if not value and not data:
            raise ClickException("Empty transaction (neither value nor data specified)")

        tx, w3 = create_tx_from_args(
            w3,
            rpc_endpoint,
            from_addr=from_addr,
            to_addr=to_addr,
            value=value,
            data=data,
            gas=gas,
            gas_price=gas_price,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            fee_factor=fee_factor,
            nonce=nonce,
            chain_id=chain_id,
        )

    # Fill in any missing values.

    tx = finalize_tx_from_args(w3, rpc_endpoint, tx, from_addr)

    # If the --legacy flag was given, explicitly set the type,
    # otherwise have web3 determine it.

    if legacy:
        tx["type"] = HexStr("0x0")

    print(to_json(tx))


tx_group.add_command(make)


@command()
@rpc_endpoint_option
@argument("tx-file", type=Path())
def send(rpc_endpoint: Optional[str], tx_file: str) -> None:
    """
    Send raw transaction (as generated by `tx sign`) contained in the given file.

    Use '-' to read from standard input instead of a file.
    Outputs the transaction hash if it is successfully sent.
    """

    signed_tx = SignedTransaction(**json.loads(load_from_file_or_stdin(tx_file)))
    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    tx_hash = send_tx(w3, signed_tx)
    print(Web3.to_hex(tx_hash))


tx_group.add_command(send)


@command()
@rpc_endpoint_option
@option("--quiet", "-q", is_flag=True, help="do not print the transaction receipt.")
@option(
    "--timeout",
    "-t",
    type=float,
    help="wait up to some (decimal) number of seconds.",
)
@argument("tx-hash", required=True)
def wait(
    rpc_endpoint: Optional[str], quiet: bool, timeout: Optional[float], tx_hash: str
) -> None:
    """
    Wait for a transaction with a specific hash, and print the receipt.

    The command will return exit code 0 if the transaction
    succeeded, or non-zero otherwise.

    Timeout also results in a non-zero exit code.
    """

    hash_bytes = HexBytes(validate_32byte_hash_string(tx_hash))

    try:
        w3 = web3_from_endpoint_arg(None, rpc_endpoint)
        tx_receipt = wait_for_tx(w3, hash_bytes, timeout=timeout)
        if not quiet:
            print(to_json(tx_receipt))

        if tx_receipt["status"] == 0:
            raise ClickException("Transaction failed")

    except asyncio.TimeoutError:
        raise ClickException(  # pylint: disable=raise-missing-from
            f"Transaction {tx_hash} timed out"
        )


tx_group.add_command(wait)
