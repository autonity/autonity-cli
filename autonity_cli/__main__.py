"""
Autonity RPC Client
"""

import sys

from autonity.contracts.autonity import __version__ as protocol_version
from click import group, option, version_option

from .commands import (
    account,
    block,
    contract,
    governance,
    node,
    protocol,
    token,
    tx,
    validator,
)
from .logging import enable_logging


@group(context_settings=dict(help_option_names=["-h", "--help"]))
@option("--verbose", "-v", is_flag=True, help="Enable additional output (to stderr)")
@version_option(
    message=f"%(prog)s, version %(version)s\nprotocol version {protocol_version}"
)
def aut(verbose: bool) -> None:
    """
    Command line interface to interact with Autonity.
    """

    if verbose:
        enable_logging()
    else:
        # Do not print the full callstack
        sys.tracebacklimit = 0


aut.add_command(node.node_group)
aut.add_command(block.block_group)
aut.add_command(tx.tx_group)
aut.add_command(protocol.protocol_group)
aut.add_command(governance.governance_group)
aut.add_command(validator.validator)
aut.add_command(account.account_group)
aut.add_command(token.token_group)
aut.add_command(contract.contract_group)
