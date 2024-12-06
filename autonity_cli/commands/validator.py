"""
The `validator` command group.
"""

import sys
from dataclasses import asdict
from typing import Optional
from urllib import parse as urlparse

from autonity import Autonity, LiquidLogic
from click import argument, command, echo, group, option
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3 import Web3
from web3.exceptions import ContractLogicError

from .protocol import protocol_group
from ..config import get_node_address
from ..constants import UnixExitStatus
from ..denominations import format_auton_quantity
from ..options import (
    from_option,
    keyfile_option,
    rpc_endpoint_option,
    tx_aux_options,
    validator_option,
)
from ..utils import (
    autonity_from_endpoint_arg,
    create_contract_tx_from_args,
    from_address_from_argument,
    parse_commission_rate,
    parse_newton_value_representation,
    to_json,
    web3_from_endpoint_arg,
)

# Disable pylint warning about imports outside top-level.  We do this
# intentionally to try and keep startup times of the CLI low.

# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

# TODO: consider caching the LNTN addresses of Validators


@group()
def validator() -> None:
    """
    Commands related to the validators.
    """


validator.add_command(
    protocol_group.get_command(None, "validators"),  # type: ignore
    name="list",
)


@command()
@rpc_endpoint_option
@validator_option
def info(rpc_endpoint: Optional[str], validator_addr_str: str) -> None:
    """
    Get information about a validator.
    """

    validator_addr = get_node_address(validator_addr_str)
    aut = autonity_from_endpoint_arg(rpc_endpoint)
    try:
        validator_data = aut.get_validator(validator_addr)
    except ContractLogicError:
        echo(
            f"The address {validator_addr} is not registered as a validator.",
            err=True,
        )
        sys.exit(UnixExitStatus.WEB3_RESOURCE_NOT_FOUND)
    echo(to_json(asdict(validator_data), pretty=True))


validator.add_command(info)


@command()
@argument("enode")
def compute_address(
    enode: str,
) -> None:
    """
    Compute the address corresponding to an enode URL.
    """

    _, key_at_ip_port, _, _, _, _ = urlparse.urlparse(enode)
    pubkey, _ = key_at_ip_port.split("@")
    addr_bytes = Web3.keccak(bytes(HexBytes(pubkey)))[-20:]
    print(Web3.to_checksum_address(addr_bytes.hex()))


validator.add_command(compute_address)


@command()
@rpc_endpoint_option
@keyfile_option()
@from_option
@tx_aux_options
@validator_option
@argument("amount-str", metavar="AMOUNT", nargs=1)
def bond(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
    amount_str: str,
) -> None:
    """
    Bond Newton to a validator.
    """

    token_units = parse_newton_value_representation(amount_str)
    validator_addr = get_node_address(validator_addr_str)
    from_addr = from_address_from_argument(from_str, keyfile)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.bond(validator_addr, token_units),
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )
    print(to_json(tx))


validator.add_command(bond)


@command()
@rpc_endpoint_option
@keyfile_option()
@from_option
@tx_aux_options
@validator_option
@argument("amount-str", metavar="AMOUNT", nargs=1)
def unbond(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
    amount_str: str,
) -> None:
    """
    Unbond Newton from a validator.
    """

    token_units = parse_newton_value_representation(amount_str)
    validator_addr = get_node_address(validator_addr_str)
    from_addr = from_address_from_argument(from_str, keyfile)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.unbond(validator_addr, token_units),
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )
    print(to_json(tx))


validator.add_command(unbond)


@command()
@rpc_endpoint_option
@keyfile_option()
@from_option
@tx_aux_options
@argument("enode")
@argument("oracle")
@argument("consensus_key")
@argument("proof")
def register(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    enode: str,
    oracle: ChecksumAddress,
    consensus_key: str,
    proof: str,
) -> None:
    """
    Register a validator.
    """

    consensus_key_bytes = HexBytes(consensus_key)
    proof_bytes = HexBytes(proof)

    from_addr = from_address_from_argument(from_str, keyfile)
    # TODO: validate enode string?

    aut = autonity_from_endpoint_arg(rpc_endpoint)
    tx = create_contract_tx_from_args(
        function=aut.register_validator(
            enode, oracle, consensus_key_bytes, proof_bytes
        ),
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )
    print(to_json(tx))


validator.add_command(register)


@command()
@rpc_endpoint_option
@keyfile_option()
@from_option
@tx_aux_options
@validator_option
def pause(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
) -> None:
    """
    Pause the given validator.

    See `pauseValidator` on the Autonity contract.
    """

    validator_addr = get_node_address(validator_addr_str)
    from_addr = from_address_from_argument(from_str, keyfile)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.pause_validator(validator_addr),
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )
    print(to_json(tx))


validator.add_command(pause)


@command()
@rpc_endpoint_option
@keyfile_option()
@from_option
@tx_aux_options
@validator_option
def activate(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
) -> None:
    """
    Activate a paused validator.

    See `activateValidator` on the Autonity contract.
    """

    validator_addr = get_node_address(validator_addr_str)
    from_addr = from_address_from_argument(from_str, keyfile)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.activate_validator(validator_addr),
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )
    print(to_json(tx))


validator.add_command(activate)


@command()
@rpc_endpoint_option
@keyfile_option()
@from_option
@tx_aux_options
@validator_option
@argument("rate", type=str, nargs=1)
def change_commission_rate(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
    rate: str,
) -> None:
    """
    Change the commission rate for the given validator.

    The rate is given as a decimal, and must be no greater than 1 e.g. 3% would be 0.03.
    """

    validator_addr = get_node_address(validator_addr_str)
    from_addr = from_address_from_argument(from_str, keyfile)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    rate_int = parse_commission_rate(rate)

    tx = create_contract_tx_from_args(
        function=aut.change_commission_rate(validator_addr, rate_int),
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )
    print(to_json(tx))


validator.add_command(change_commission_rate)


@command()
@rpc_endpoint_option
@keyfile_option()
@validator_option
@option("--account", help="Delegator account to check")
def unclaimed_rewards(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    validator_addr_str: Optional[str],
    account: Optional[str],
) -> None:
    """
    Check the given validator for unclaimed fees.
    """

    validator_addr = get_node_address(validator_addr_str)
    account = from_address_from_argument(account, keyfile)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)

    aut = Autonity(w3)
    validator = aut.get_validator(validator_addr)
    liquid_newton = LiquidLogic(w3, validator.liquid_state_contract)
    unclaimed_atn = liquid_newton.unclaimed_rewards(account)
    print(format_auton_quantity(unclaimed_atn))


validator.add_command(unclaimed_rewards)


@command()
@rpc_endpoint_option
@keyfile_option()
@from_option
@tx_aux_options
@validator_option
def claim_rewards(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
) -> None:
    """
    Claim rewards from a validator.
    """

    validator_addr = get_node_address(validator_addr_str)
    from_addr = from_address_from_argument(from_str, keyfile)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    aut = Autonity(w3)
    validator = aut.get_validator(validator_addr)
    liquid_newton = LiquidLogic(w3, validator.liquid_state_contract)

    tx = create_contract_tx_from_args(
        function=liquid_newton.claim_rewards(),
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )
    print(to_json(tx))


validator.add_command(claim_rewards)


@command()
@rpc_endpoint_option
@keyfile_option()
@from_option
@tx_aux_options
@validator_option
@argument("enode", nargs=1)
def update_enode(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
    enode: str,
) -> None:
    """
    Update the enode of a registered validator.

    This function updates the network connection information (IP or/and port)
    of a registered validator. You cannot change the validator's address
    (pubkey part of the enode).
    """

    validator_addr = get_node_address(validator_addr_str)
    from_addr = from_address_from_argument(from_str, keyfile)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.update_enode(validator_addr, enode),
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )
    print(to_json(tx))


validator.add_command(update_enode)
