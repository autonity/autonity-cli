from typing import Optional

from click import argument, group
from web3 import Web3

from autonity_cli.auth import validate_authenticator_account

from ..options import from_options, rpc_endpoint_option, tx_aux_options
from ..utils import (
    autonity_from_endpoint_arg,
    create_contract_tx_from_args,
    parse_newton_value_representation,
    parse_wei_representation,
    to_json,
)


@group(name="governance")
def governance_group() -> None:
    """
    Commands that can only be called by the governance operator account.
    """


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("schedule-vault", metavar="ADDRESS")
@argument("amount", type=int)
@argument("start-time", type=int)
@argument("total-duration", type=int)
def create_schedule(
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
    schedule_vault: str,
    amount: int,
    start_time: int,
    duration: int,
) -> None:
    """
    Create a new schedule.

    Restricted to the Operator account. See `createSchedule` on Autonity contract.
    """

    vault_address = Web3.to_checksum_address(schedule_vault)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.create_schedule(vault_address, amount, start_time, duration),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("duration", type=int, nargs=1)
def set_max_schedule_duration(
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
    duration: int,
) -> None:
    """
    Set the maximum allowed duration of any schedule or contract.

    Restricted to the operator account.
    See `setMaxScheduleDuration` on Autonity contract.
    """

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_max_schedule_duration(duration),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("committee-size", type=int, nargs=1)
def set_committee_size(
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
    committee_size: int,
) -> None:
    """
    Set the maximum size of the consensus committee.

    Restricted to the Operator account. See `setCommitteeSize` on Autonity contract.
    """

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_committee_size(committee_size),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("unbonding-period", type=int, nargs=1)
def set_unbonding_period(
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
    unbonding_period: int,
) -> None:
    """
    Set the unbonding period.

    Restricted to the Operator account. See `setUnbondingPeriod` on Autonity contract.
    """

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_unbonding_period(unbonding_period),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("proposer-reward-rate", type=int)
def set_proposer_reward_rate(
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
    proposer_reward_rate: int,
):
    """
    Set the proposer reward rate for the policy configuration.

    Restricted to the Operator account.
    See `setProposerRewardRate` on Autonity contract.
    """

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_proposer_reward_rate(proposer_reward_rate),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("oracle-reward-rate", type=int)
def set_oracle_reward_rate(
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
    oracle_reward_rate: int,
):
    """
    Set the unbonding period.

    Restricted to the Operator account. See `setOracleRewardRate` on Autonity contract.
    """

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_oracle_reward_rate(oracle_reward_rate),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("withholding_threshold", type=int)
def set_withholding_threshold(
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
    withholding_threshold: int,
):
    """
    Set the withholding threshold for the policy configuration.

    Restricted to the Operator account.
    See `setWithholdingThreshold` on Autonity contract.
    """

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_withholding_threshold(withholding_threshold),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("pool-address-str", metavar="POOL-ADDRESS")
def set_withheld_rewards_pool(
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
    pool_address_str: str,
):
    """
    Set the address of the pool to which withheld rewards will be sent.

    Restricted to the Operator account.
    See `setWithheldRewardsPool` on Autonity contract.
    """

    pool_address = Web3.to_checksum_address(pool_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_withheld_rewards_pool(pool_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("epoch-period", type=int, nargs=1)
def set_epoch_period(
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
    epoch_period: int,
) -> None:
    """
    Set the epoch period.

    Restricted to the Operator account. See `setEpochPeriod` on Autonity contract.
    """

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_epoch_period(epoch_period),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("operator-address-str", metavar="OPERATOR-ADDRESS", nargs=1)
def set_operator_account(
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
    operator_address_str: str,
) -> None:
    """
    Set the Operator account.

    Restricted to the Operator account. See `setOperatorAccount` on Autonity contract.
    """

    operator_address = Web3.to_checksum_address(operator_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_operator_account(operator_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("treasury-address-str", metavar="treasury-address", nargs=1)
def set_treasury_account(
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
    treasury_address_str: str,
) -> None:
    """
    Set the global treasury account.

    Restricted to the Operator account. See `setTreasuryAccount` on Autonity contract.
    """

    treasury_address = Web3.to_checksum_address(treasury_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_treasury_account(treasury_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("treasury-fee-str", metavar="TREASURY-FEE", nargs=1)
def set_treasury_fee(
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
    treasury_fee_str: str,
) -> None:
    """
    Set the treasury fee.

    Restricted to the Operator account. See `setTreasuryFee` on Autonity contract.
    """

    treasury_fee = parse_wei_representation(treasury_fee_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_treasury_fee(treasury_fee),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS", nargs=1)
def set_accountability_contract(
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
    contract_address_str: str,
) -> None:
    """
    Set the Accountability contract address.

    Restricted to the Operator account.
    See `setAccountabilityContract` on Autonity contract.
    """

    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_accountability_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS", nargs=1)
def set_oracle_contract(
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
    contract_address_str: str,
) -> None:
    """
    Set the Oracle contract address.

    Restricted to the Operator account. See `setOracleContract` on Autonity contract.
    """

    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_oracle_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS", nargs=1)
def set_acu_contract(
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
    contract_address_str: str,
) -> None:
    """
    Set the ACU contract address.

    Restricted to the Operator account. See `setAcuContract` on Autonity contract.
    """

    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_acu_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS", nargs=1)
def set_supply_control_contract(
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
    contract_address_str: str,
) -> None:
    """
    Set the Supply Control contract address.

    Restricted to the Operator account.
    See `setSupplyControlContract` on Autonity contract.
    """

    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_supply_control_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS", nargs=1)
def set_stabilization_contract(
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
    contract_address_str: str,
) -> None:
    """
    Set the Stabilization contract address.

    Restricted to the Operator account.
    See `setSupplyControlContract` on Autonity contract.
    """

    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_stabilization_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS", nargs=1)
def set_inflation_controller_contract(
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
    contract_address_str: str,
) -> None:
    """
    Set the Inflation Controller contract address.

    Restricted to the Operator account.
    See `setInflationControllerContract` on Autonity contract.
    """

    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_inflation_controller_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS", nargs=1)
def set_omission_accountability_contract(
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
    contract_address_str: str,
) -> None:
    """
    Set the Omission Accountability contract address.

    Restricted to the Operator account.
    See `setOmissionAccountabilityContract` on Autonity contract.
    """

    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_omission_accountability_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS", nargs=1)
def set_liquid_logic_contract(
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
    contract_address_str: str,
) -> None:
    """
    Set the Liquid Logic contract address.

    Restricted to the Operator account.
    See `setAccountabilityContract` on Autonity contract.
    """

    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_liquid_logic_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS")
def set_auctioneer_contract(
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
    contract_address_str: str,
):
    """
    Set the Auctioneer contract address.

    Restricted to the Operator account. See `setAuctioneerContract` on Autonity
    contract.
    """
    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_auctioneer_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("contract-address-str", metavar="CONTRACT-ADDRESS")
def set_upgrade_manager_contract(
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
    contract_address_str: str,
):
    """
    Set the Upgrade Manager contract address.

    Restricted to the Operator account. See `setUpgradeManagerContract` on Autonity
    contract.
    """
    contract_address = Web3.to_checksum_address(contract_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_upgrade_manager_contract(contract_address),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("amount-str", metavar="AMOUNT", nargs=1)
@argument("recipient-str", metavar="RECIPIENT", required=False)
def mint(
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
    amount_str: str,
    recipient_str: Optional[str],
) -> None:
    """
    Mint new stake token (NTN) and add it to the recipient's balance.

    If recipient is not specified, the caller's address is used.
    Restricted to the Operator account. See `mint` on Autonity contract.
    """

    token_units = parse_newton_value_representation(amount_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    recipient = Web3.to_checksum_address(recipient_str) if recipient_str else from_addr

    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.mint(recipient, token_units),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("amount-str", metavar="AMOUNT")
@argument("account-str", metavar="ACCOUNT", required=False)
def burn(
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
    amount_str: str,
    account_str: Optional[str],
) -> None:
    """
    Burn the specified amount of NTN stake token from an account.

    If account is not specified, the caller's address is used.
    This won't burn associated Liquid tokens.
    Restricted to the Operator account. See `burn` on Autonity contract.
    """

    token_units = parse_newton_value_representation(amount_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    account = Web3.to_checksum_address(account_str) if account_str else from_addr
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.burn(account, token_units),
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


@governance_group.command()
@rpc_endpoint_option
@from_options()
@tx_aux_options
@argument("slasher-address-str", metavar="SLASHER-ADDRESS")
def set_slasher(
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
    slasher_address_str: str,
):
    """
    Set the slasher account.

    Restricted to the Operator account. See `setSlasher` on Autonity contract.
    """
    slasher_address = Web3.to_checksum_address(slasher_address_str)
    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)
    aut = autonity_from_endpoint_arg(rpc_endpoint)

    tx = create_contract_tx_from_args(
        function=aut.set_slasher(slasher_address),
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
