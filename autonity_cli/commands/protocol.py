"""
The `protocol` command group.
"""

from typing import Any, Optional, Sequence

from autonity import Autonity
from autonity.constants import AUTONITY_CONTRACT_ADDRESS
from click import argument, command, echo, group

from ..options import rpc_endpoint_option
from ..utils import autonity_from_endpoint_arg, to_json, web3_from_endpoint_arg

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals


@group(name="protocol")
def protocol_group() -> None:
    """
    Commands related to Autonity-specific protocol operations.  See
    the Autonity contract reference for details.
    """


def _show_sequence(value: Sequence[Any]) -> str:
    return "\n".join([str(v) for v in value])


def _show_json(value: Any) -> str:

    return to_json(value, pretty=True)


@command()
@rpc_endpoint_option
def commission_rate_precision(rpc_endpoint: Optional[str]) -> None:
    """
    Precision of validator commission rate values
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).commission_rate_precision())


protocol_group.add_command(commission_rate_precision)


@command()
@rpc_endpoint_option
def max_bond_applied_gas(rpc_endpoint: Optional[str]) -> None:
    """
    Max allowed gas for notifying delegator about bonding
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).max_bond_applied_gas())


protocol_group.add_command(max_bond_applied_gas)


@command()
@rpc_endpoint_option
def max_unbond_applied_gas(rpc_endpoint: Optional[str]) -> None:
    """
    Max allowed gas for notifying delegator about unbonding
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).max_unbond_applied_gas())


protocol_group.add_command(max_unbond_applied_gas)


@command()
@rpc_endpoint_option
def max_unbond_released_gas(rpc_endpoint: Optional[str]) -> None:
    """
    Max allowed gas for notifying delegator about bond being released
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).max_unbond_released_gas())


protocol_group.add_command(max_unbond_released_gas)


@command()
@rpc_endpoint_option
def max_rewards_distribution_gas(rpc_endpoint: Optional[str]) -> None:
    """
    Max allowed gas for notifying delegator about rewards being distributed
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).max_rewards_distribution_gas())


protocol_group.add_command(max_rewards_distribution_gas)


@command()
@rpc_endpoint_option
def config(rpc_endpoint: Optional[str]) -> None:
    """
    Print the Autonity contract config
    """

    print(_show_json(autonity_from_endpoint_arg(rpc_endpoint).config()))


protocol_group.add_command(config)


@command()
@rpc_endpoint_option
def epoch_id(rpc_endpoint: Optional[str]) -> None:
    """
    ID of current epoch
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).epoch_id())


protocol_group.add_command(epoch_id)


@command()
@rpc_endpoint_option
def last_epoch_time(rpc_endpoint: Optional[str]) -> None:
    """
    Timestamp of the last epoch
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).last_epoch_time())


protocol_group.add_command(last_epoch_time)


@command()
@rpc_endpoint_option
def epoch_total_bonded_stake(rpc_endpoint: Optional[str]) -> None:
    """
    Total stake bonded this epoch
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).epoch_total_bonded_stake())


protocol_group.add_command(epoch_total_bonded_stake)


@command()
@rpc_endpoint_option
def atn_total_redistributed(rpc_endpoint: Optional[str]) -> None:
    """
    Total fees redistributed
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).atn_total_redistributed())


protocol_group.add_command(atn_total_redistributed)


@command()
@rpc_endpoint_option
def epoch_reward(rpc_endpoint: Optional[str]) -> None:
    """
    Reward for this epoch
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).epoch_reward())


protocol_group.add_command(epoch_reward)


@command()
@rpc_endpoint_option
def staking_gas_price(rpc_endpoint: Optional[str]) -> None:
    """
    The gas price to notify the delegator about the staking operation at epoch end
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).staking_gas_price())


protocol_group.add_command(staking_gas_price)


@command()
@rpc_endpoint_option
def inflation_reserve(rpc_endpoint: Optional[str]) -> None:
    """
    The inflation reserve
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).inflation_reserve())


protocol_group.add_command(inflation_reserve)


@command()
@rpc_endpoint_option
def deployer(rpc_endpoint: Optional[str]) -> None:
    """
    Contract deployer
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).deployer())


protocol_group.add_command(deployer)


@command()
@rpc_endpoint_option
def epoch_period(rpc_endpoint: Optional[str]) -> None:
    """Epoch period in blocks"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_epoch_period())


protocol_group.add_command(epoch_period)


@command()
@rpc_endpoint_option
def block_period(rpc_endpoint: Optional[str]) -> None:
    """Block period in seconds"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_block_period())


protocol_group.add_command(block_period)


@command()
@rpc_endpoint_option
def unbonding_period(rpc_endpoint: Optional[str]) -> None:
    """Unbonding period in blocks"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_unbonding_period())


protocol_group.add_command(unbonding_period)


@command()
@rpc_endpoint_option
def last_epoch_block(rpc_endpoint: Optional[str]) -> None:
    """
    Block number of the last epoch
    """

    print(autonity_from_endpoint_arg(rpc_endpoint).get_last_epoch_block())


protocol_group.add_command(last_epoch_block)


@command()
@rpc_endpoint_option
def version(rpc_endpoint: Optional[str]) -> None:
    """Contract version"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_version())


protocol_group.add_command(version)


@command()
@rpc_endpoint_option
def committee(rpc_endpoint: Optional[str]) -> None:
    """
    Get current committee
    """

    print(_show_json(autonity_from_endpoint_arg(rpc_endpoint).get_committee()))


protocol_group.add_command(committee)


@command()
@rpc_endpoint_option
def validators(rpc_endpoint: Optional[str]) -> None:
    """Get current validators"""

    print(_show_sequence(autonity_from_endpoint_arg(rpc_endpoint).get_validators()))


protocol_group.add_command(validators)


@command()
@rpc_endpoint_option
def treasury_account(rpc_endpoint: Optional[str]) -> None:
    """Treasury account address"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_treasury_account())


protocol_group.add_command(treasury_account)


@command()
@rpc_endpoint_option
def treasury_fee(rpc_endpoint: Optional[str]) -> None:
    """Treasury fee"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_treasury_fee())


protocol_group.add_command(treasury_fee)


@command()
@rpc_endpoint_option
def max_committee_size(rpc_endpoint: Optional[str]) -> None:
    """Maximum committee size"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_max_committee_size())


protocol_group.add_command(max_committee_size)


@command()
@rpc_endpoint_option
def committee_enodes(rpc_endpoint: Optional[str]) -> None:
    """Enodes in current committee"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_committee_enodes())


protocol_group.add_command(committee_enodes)


@command()
@rpc_endpoint_option
def minimum_base_fee(rpc_endpoint: Optional[str]) -> None:
    """Minimum base fee"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_minimum_base_fee())


protocol_group.add_command(minimum_base_fee)


@command()
@rpc_endpoint_option
def operator(rpc_endpoint: Optional[str]) -> None:
    """The governance operator"""

    print(autonity_from_endpoint_arg(rpc_endpoint).get_operator())


protocol_group.add_command(operator)


@command()
@rpc_endpoint_option
@argument("unbonding_id", type=int, nargs=1)
def get_unbonding_release_state(rpc_endpoint: Optional[str], unbonding_id: int) -> None:
    """Get the release state of the unbonding request"""

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(aut.get_unbonding_release_state(unbonding_id))


protocol_group.add_command(get_unbonding_release_state)


@command()
@rpc_endpoint_option
@argument("unbonding_id", type=int, nargs=1)
def reverting_amount(rpc_endpoint: Optional[str], unbonding_id: int) -> None:
    """
    Get the amount of LNTN or NTN bonded when the released unbonding was reverted
    """

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(aut.get_reverting_amount(unbonding_id))


protocol_group.add_command(reverting_amount)


@command()
@rpc_endpoint_option
@argument("block", type=int, nargs=1)
def epoch_from_block(rpc_endpoint: Optional[str], block: int) -> None:
    """Get the epoch of the given block"""

    aut = Autonity(web3_from_endpoint_arg(None, rpc_endpoint))
    print(aut.get_epoch_from_block(block))


protocol_group.add_command(epoch_from_block)


@command()
def contract_address() -> None:
    """
    Address of the Autonity Contract
    """

    echo(AUTONITY_CONTRACT_ADDRESS, nl=False)


protocol_group.add_command(contract_address)
