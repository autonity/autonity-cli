"""
The `tx` command group.
"""

import asyncio
import json
from typing import Optional

from autonity.erc20 import ERC20
from autonity.utils.tx import send_tx, wait_for_tx
from click import ClickException, Path, argument, command, group, option
from eth_account.account import SignedTransaction
from eth_typing import ChecksumAddress, HexStr
from hexbytes import HexBytes
from web3 import Web3
from web3.types import Wei

from ..commands.account import signtx
from ..logging import log
from ..options import (
    config_option,
    from_option,
    keyfile_option,
    newton_or_token_option,
    rpc_endpoint_option,
    tx_aux_options,
    tx_value_option,
)
from ..param_types import ChecksumAddressType, HexBytesType
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
)

# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments


@group(name="tx")
def tx_group() -> None:
    """Commands for transaction creation and processing."""


# Re-use the `account signtx` command as `tx sign`
tx_group.add_command(signtx, name="sign")


@command()
@config_option
@rpc_endpoint_option
@newton_or_token_option
@keyfile_option()
@from_option
@option(
    "--to", "-t", type=ChecksumAddressType(), help="Address to which tx is directed."
)
@tx_value_option(required=True)
@tx_aux_options
@option(
    "--data",
    "-d",
    type=HexBytesType(),
    help="Compiled contract code OR method signature and parameters.",
)
@option(
    "--legacy",
    is_flag=True,
    help="If set, tx type is 0x0 (pre-EIP1559), otherwise type is 0x2.",
)
def make(
    w3: Web3,
    ntn: bool,
    token: Optional[ChecksumAddress],
    keyfile: Optional[str],
    from_: Optional[ChecksumAddress],
    to: Optional[ChecksumAddress],
    gas: Optional[int],
    gas_price: Optional[Wei],
    max_priority_fee_per_gas: Optional[Wei],
    max_fee_per_gas: Optional[Wei],
    fee_factor: Optional[float],
    nonce: Optional[int],
    value: str,
    data: Optional[HexBytes],
    chain_id: Optional[int],
    legacy: bool,
) -> None:
    """Create a transaction given the parameters passed in."""

    # TODO: Add a flag which results in only unconnected Web3
    # instances being created.  Callers who do not want to connect to
    # a node will then receive an error if they do not specify all
    # required values (rather than having Web3.py silently connect).

    # If from_str is not set, take the address from a keyfile instead
    # (if given)
    from_addr = from_address_from_argument_optional(from_, keyfile)
    log(f"from_addr: {from_addr}")

    to_addr = to if to else None

    if to_addr is None:
        raise ClickException(
            "To-address must be specified "
            "(use the `contract deploy` command to deploy a contract)"
        )

    token_addresss = newton_or_token_to_address(ntn, token)

    # If --fee-factor was given, we must do some computation up-front

    # If this is a token call, fill in the "to" and "data" fields
    # using the contract call.  Otherwise, for a plain AUT transfer,
    # use create_transaction and finalize_transaction wrappers.

    if token_addresss:
        if not from_addr:
            raise ClickException("From address not given")

        erc = ERC20(w3, token_addresss)
        token_units = parse_token_value_representation(value, erc.decimals())
        function = erc.transfer(recipient=to_addr, amount=token_units)
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
            raise ClickException("From address not given")

        if not value and not data:
            raise ClickException("Empty tx (neither value or data given)")

        tx = create_tx_from_args(
            w3,
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

    tx = finalize_tx_from_args(w3, tx, from_addr)

    # If the --legacy flag was given, explicitly set the type,
    # otherwise have web3 determine it.

    if legacy:
        tx["type"] = HexStr("0x0")

    print(to_json(tx))


tx_group.add_command(make)


@command()
@config_option
@rpc_endpoint_option
@argument("tx-file", type=Path())
def send(w3: Web3, tx_file: str) -> None:
    """Send raw transaction (as generated by signtx).

    The raw transaction is read from the given file.
    Use '-' to read from stdin instead of a file.
    Outputs the transaction hash if it is successfully sent.
    """

    signed_tx = SignedTransaction(**json.loads(load_from_file_or_stdin(tx_file)))
    tx_hash = send_tx(w3, signed_tx)
    print(Web3.to_hex(tx_hash))


tx_group.add_command(send)


@command()
@config_option
@rpc_endpoint_option
@option("--quiet", "-q", is_flag=True, help="Do not dump the full transaction receipt.")
@option(
    "--timeout",
    "-t",
    type=float,
    help="Wait up to some (non-whole) number of seconds.",
)
@argument("tx-hash", required=True)
def wait(w3: Web3, quiet: bool, timeout: Optional[float], tx_hash: str) -> None:
    """Wait for a transaction with a specific hash, and print the receipt.

    The command will return exit code 0 if the transaction
    succeeded, or non-zero otherwise.

    Timeouts also result in a non-zero exit code.
    """

    hash_bytes = HexBytes(validate_32byte_hash_string(tx_hash))

    try:
        tx_receipt = wait_for_tx(w3, hash_bytes, timeout=timeout)
        if not quiet:
            print(to_json(tx_receipt))

        if tx_receipt["status"] == 0:
            raise ClickException("Transaction failed")

    except asyncio.TimeoutError:
        raise ClickException(  # pylint: disable=raise-missing-from
            "Tx {tx_hash} timed out"
        )


tx_group.add_command(wait)
