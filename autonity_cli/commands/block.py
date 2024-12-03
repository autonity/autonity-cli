"""
The "block" command group
"""

from typing import Optional

from click import argument, command, group

from ..options import rpc_endpoint_option
from ..user import get_block
from ..utils import to_json, validate_block_identifier, web3_from_endpoint_arg


@group(name="block")
def block_group() -> None:
    """
    Commands for querying block information.
    """


@command()
@rpc_endpoint_option
@argument("identifier", default="latest")
def get(rpc_endpoint: Optional[str], identifier: str) -> None:
    """
    Print information for block.

    <identifier> is a block number or hash. If no argument is given, "latest" is used.
    """

    block_id = validate_block_identifier(identifier)
    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    block_data = get_block(w3, block_id)
    print(to_json(block_data))


block_group.add_command(get)


@command()
@rpc_endpoint_option
def height(rpc_endpoint: Optional[str]) -> None:
    """
    Print the current block height for the chain.
    """

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    print(w3.eth.block_number)


block_group.add_command(height)
