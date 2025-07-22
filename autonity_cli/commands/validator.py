import sys
from dataclasses import asdict
from typing import Optional
from urllib import parse as urlparse

from autonity import Autonity, LiquidLogic
from click import argument, echo, group, option
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3 import Web3
from web3.exceptions import ContractLogicError

from ..auth import validate_authenticator_account
from ..config import get_node_address
from ..constants import UnixExitStatus
from ..denominations import format_auton_quantity, format_newton_quantity
from ..options import (
    authentication_options,
    from_options,
    rpc_endpoint_option,
    tx_aux_options,
    validator_option,
)
from ..utils import (
    autonity_from_endpoint_arg,
    create_contract_tx_from_args,
    parse_commission_rate,
    parse_newton_value_representation,
    to_json,
    web3_from_endpoint_arg,
)
from .protocol import protocol_group

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


@validator.command()
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


@validator.command()
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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
@argument("amount-str", metavar="AMOUNT", nargs=1)
def bond(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
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
    Create a bonding (delegation) request with the sender as delegator.

    The sender is the configured From address.
    """

    token_units = parse_newton_value_representation(amount_str)
    validator_addr = get_node_address(validator_addr_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("caller-str", metavar="CALLER")
@argument("amount-str", metavar="AMOUNT")
def approve_bonding(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    account_str: str,
    amount_str: str,
) -> None:
    """
    Set AMOUNT as the bonding allowance in NTN of ACCOUNT over the sender's tokens.

    The sender is the configured From address.
    """

    account_address = Web3.to_checksum_address(account_str)
    token_units = parse_newton_value_representation(amount_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.approve_bonding(account_address, token_units),
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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
@argument("account-str", metavar="ACCOUNT")
@argument("amount-str", metavar="AMOUNT")
def bond_from(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
    account_str: str,
    amount_str: str,
) -> None:
    """
    Create a bonding (delegation) request with ACCOUNT as delegator. The sender
    needs to have the required bonding allowance to bond NTN to ACCOUNT.

    The sender is the configured From address.
    """

    token_units = parse_newton_value_representation(amount_str)
    account_addr = Web3.to_checksum_address(account_str)
    validator_addr = get_node_address(validator_addr_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.bond_from(account_addr, validator_addr, token_units),
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


@validator.command()
@rpc_endpoint_option
@authentication_options()
@option("--account", help="Account to check (defaults to From address)")
@argument("owner-str", metavar="OWNER")
def bonding_allowance(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    validator_addr_str: Optional[str],
    account: Optional[str],
    owner_str: str,
) -> None:
    """
    The remaining NTN quantity that ACCOUNT will be allowed to bond on behalf of OWNER
    through `bond-from`.
    """

    account = validate_authenticator_account(account, keyfile=keyfile, trezor=trezor)
    owner_address = Web3.to_checksum_address(owner_str)

    aut = autonity_from_endpoint_arg(rpc_endpoint)
    allowance = aut.bonding_allowance(owner_address, account)
    print(format_newton_quantity(allowance))


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
@argument("amount-str", metavar="AMOUNT", nargs=1)
def unbond(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
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
    Create an unbonding request with the sender as delegator.

    The sender is the configured From address.
    """

    token_units = parse_newton_value_representation(amount_str)
    validator_addr = get_node_address(validator_addr_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
@argument("caller-str", metavar="CALLER")
@argument("amount-str", metavar="AMOUNT")
def approve_unbonding(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
    account_str: str,
    amount_str: str,
) -> None:
    """
    Set AMOUNT as the unbonding allowance in LNTN of ACCOUNT over the sender's tokens.

    The sender is the configured From address.
    """

    validator_address = get_node_address(validator_addr_str)
    account_address = Web3.to_checksum_address(account_str)
    token_units = parse_newton_value_representation(amount_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)

    aut = Autonity(w3)
    validator = aut.get_validator(validator_address)
    liquid_newton = LiquidLogic(w3, validator.liquid_state_contract)

    tx = create_contract_tx_from_args(
        function=liquid_newton.approve_unbonding(account_address, token_units),
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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
@argument("account-str", metavar="ACCOUNT")
@argument("amount-str", metavar="AMOUNT")
def unbond_from(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    validator_addr_str: Optional[str],
    account_str: str,
    amount_str: str,
) -> None:
    """
    Create an unbonding request with ACCOUNT as delegator. The sender needs to have the
    required unbonding allowance to unbond LNTN from ACCOUNT.

    The sender is the configured From address.
    """

    token_units = parse_newton_value_representation(amount_str)
    account_addr = Web3.to_checksum_address(account_str)
    validator_addr = get_node_address(validator_addr_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.unbond_from(account_addr, validator_addr, token_units),
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


@validator.command()
@rpc_endpoint_option
@authentication_options()
@validator_option
@option("--account", help="Account to check (defaults to From address)")
@argument("owner-str", metavar="OWNER")
def unbonding_allowance(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    validator_addr_str: Optional[str],
    account: Optional[str],
    owner_str: str,
) -> None:
    """
    The remaining LNTN quantity that ACCOUNT will be allowed to unbond on behalf of
    OWNER through `unbond-from`.
    """

    validator_addr = get_node_address(validator_addr_str)
    account = validate_authenticator_account(account, keyfile=keyfile, trezor=trezor)
    owner_address = Web3.to_checksum_address(owner_str)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)

    aut = Autonity(w3)
    validator = aut.get_validator(validator_addr)
    liquid_newton = LiquidLogic(w3, validator.liquid_state_contract)
    allowance = liquid_newton.unbonding_allowance(owner_address, account)
    print(format_newton_quantity(allowance))


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("enode")
@argument("oracle")
@argument("consensus_key")
@argument("proof")
def register(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
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

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
def pause(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
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
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
def activate(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
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
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
@argument("rate", type=str, nargs=1)
def change_commission_rate(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
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
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

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


@validator.command()
@rpc_endpoint_option
@authentication_options()
@validator_option
@option("--account", help="Delegator account to check (defaults to From address)")
def unclaimed_rewards(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    validator_addr_str: Optional[str],
    account: Optional[str],
) -> None:
    """
    Check the given validator for unclaimed fees.
    """

    validator_addr = get_node_address(validator_addr_str)
    account = validate_authenticator_account(account, keyfile=keyfile, trezor=trezor)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)

    aut = Autonity(w3)
    validator = aut.get_validator(validator_addr)
    liquid_newton = LiquidLogic(w3, validator.liquid_state_contract)
    unclaimed_atn = liquid_newton.unclaimed_rewards(account)
    print(format_auton_quantity(unclaimed_atn))


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
def claim_rewards(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
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
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

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


@validator.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@validator_option
@argument("enode", nargs=1)
def update_enode(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
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
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

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


@validator.command()
@rpc_endpoint_option
@authentication_options()
@validator_option
@option("--account", help="Account to check (defaults to From address)")
def locked_balance_of(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    validator_addr_str: Optional[str],
    account: Optional[str],
) -> None:
    """
    The amount of locked Liquid Newtons held by the account in the
    given validator's Liquid Newton contract.
    """

    validator_addr = get_node_address(validator_addr_str)
    account = validate_authenticator_account(account, keyfile=keyfile, trezor=trezor)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)

    aut = Autonity(w3)
    validator = aut.get_validator(validator_addr)
    liquid_newton = LiquidLogic(w3, validator.liquid_state_contract)
    locked_balance = liquid_newton.locked_balance_of(account)
    print(format_newton_quantity(locked_balance))


@validator.command()
@rpc_endpoint_option
@authentication_options()
@validator_option
@option("--account", help="Account to check (defaults to From address)")
def unlocked_balance_of(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    validator_addr_str: Optional[str],
    account: Optional[str],
) -> None:
    """
    The amount of unlocked Liquid Newtons held by the account in the
    given validator's Liquid Newton contract.
    """

    validator_addr = get_node_address(validator_addr_str)
    account = validate_authenticator_account(account, keyfile=keyfile, trezor=trezor)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)

    aut = Autonity(w3)
    validator = aut.get_validator(validator_addr)
    liquid_newton = LiquidLogic(w3, validator.liquid_state_contract)
    unlocked_balance = liquid_newton.unlocked_balance_of(account)
    print(format_newton_quantity(unlocked_balance))
