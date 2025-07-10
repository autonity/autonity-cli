"""
Command line option sets used by multiple commands.
"""

import dataclasses
from typing import Any, Callable, Iterable, Optional, TypeVar, Union

import click
from click import Path

Func = TypeVar("Func", bound=Callable[..., Any])

Decorator = Callable[[Func], Func]


# ┌─────────────┐
# │ Option Info │
# └─────────────┘


@dataclasses.dataclass(kw_only=True)
class OptionInfo:
    args: Iterable[str]
    help: str
    # defaults should match click.Option
    required: bool = False
    metavar: Optional[str] = None
    type: Optional[Union[click.types.ParamType, Any]] = None


def make_option(option: OptionInfo, **overrides: Any) -> Decorator[Func]:
    info = dataclasses.asdict(option)
    info.update(**overrides)
    args = info.pop("args")
    return click.option(*args, **info)


keyfile_option_info = OptionInfo(
    args=(
        "--keyfile",
        "-k",
    ),
    type=Path(exists=True),
    help="encrypted private key file (falls back to 'keyfile' in config file).",
)

trezor_option_info = OptionInfo(
    args=["--trezor"],
    metavar="ACCOUNT",
    help="Trezor account index or full BIP32 derivation path",
)

# ┌─────────┐
# │ Options │
# └─────────┘

# an --rpc-endpoint, -r <url> option
rpc_endpoint_option = click.option(
    "--rpc-endpoint",
    "-r",
    metavar="URL",
    help=(
        "RPC endpoint (falls back to 'rpc_endpoint' in config file or the "
        "WEB3_ENDPOINT environment variable)."
    ),
)


def keystore_option() -> Decorator[Func]:
    """
    Option: --keystore <directory>.
    """

    def decorator(fn: Func) -> Func:
        return click.option(
            "--keystore",
            "-s",
            type=Path(exists=True),
            help=(
                "keystore directory (falls back to 'keystore' in config file, "
                "defaults to ~/.autonity/keystore)."
            ),
        )(fn)

    return decorator


def keyfile_option(required: bool = False, output: bool = False) -> Decorator[Func]:
    """
    Options: --keyfile.  If `required` is True, --keyfile is
    required.  If `output` is True, the file does not need to exist.
    """

    def decorator(fn: Func) -> Func:
        return make_option(
            keyfile_option_info, required=required, type=Path(exists=not output)
        )(fn)

    return decorator


def authentication_options() -> Decorator[Func]:
    """
    Options: --keyfile and --trezor.
    """

    def decorator(fn: Func) -> Func:
        for option in reversed(
            [
                make_option(keyfile_option_info),
                make_option(trezor_option_info),
            ]
        ):
            fn = option(fn)
        return fn

    return decorator


def newton_or_token_option(fn: Func) -> Func:
    """
    Adds the --ntn and --token flags, allowing the user to specify
    that a transfer should use an ERC20 token.
    """
    for option in reversed(
        [
            click.option("--ntn", is_flag=True, help="use Newton (NTN) as token"),
            click.option(
                "--token",
                "-t",
                metavar="TOKEN-ADDR",
                help="use the ERC20 token at the given address.",
            ),
        ]
    ):
        fn = option(fn)
    return fn


def from_options() -> Decorator[Func]:
    """Specify a 'from' address directly or via authentication options."""

    def decorator(fn: Func) -> Func:
        for option in reversed(
            [
                click.option(
                    "--from",
                    "-f",
                    "from_str",
                    metavar="ADDRESS",
                    help="the sender address.",
                ),
                make_option(keyfile_option_info),
                make_option(trezor_option_info),
            ]
        ):
            fn = option(fn)
        return fn

    return decorator


def tx_value_option(required: bool = False) -> Decorator[Func]:
    """
    Adds the --value, -v option to specify tx value field.  If `required` is True, the
    value must be provided.
    """

    def decorator(fn: Func) -> Func:
        return click.option(
            "--value",
            "-v",
            required=required,
            help=(
                "value in Auton or whole tokens "
                "(e.g. '0.000000007' and '7gwei' are identical)."
            ),
        )(fn)

    return decorator


def tx_aux_options(fn: Func) -> Func:
    """
    Remaining options which may be specified for any transaction.
      --gas
      --gas-price
      --max-fee-per-gas
      --max-priority-fee-per-gas
      --fee-factor,
      --nonce
      --chain-id
    """
    for option in reversed(
        [
            click.option(
                "--gas", "-g", help="maximum gas units that can be consumed by the tx."
            ),
            click.option(
                "--gas-price",
                "-p",
                help="value per gas in Auton (legacy, use -F and -P instead).",
            ),
            click.option(
                "--max-fee-per-gas",
                "-F",
                help="maximum to pay (in Auton) per gas for the total fee of the tx.",
            ),
            click.option(
                "--max-priority-fee-per-gas",
                "-P",
                help="maximum to pay (in Auton) per gas as tip to block proposer.",
            ),
            click.option(
                "--fee-factor",
                type=float,
                help="set maxFeePerGas to <last-basefee> x <fee-factor> [default: 2].",
            ),
            click.option(
                "--nonce",
                "-n",
                type=int,
                help="transaction nonce; query chain for account transaction count if not given.",
            ),
            click.option(
                "--chain-id",
                "-I",
                type=int,
                help="integer representing EIP155 chain ID.",
            ),
        ]
    ):
        fn = option(fn)
    return fn


def validator_option(fn: Func) -> Func:
    """
    Add the --validator <address> option to specify a validator.  Uses
    the "validator_addr_str" argument.
    """
    return click.option(
        "--validator",
        "-V",
        "validator_addr_str",
        help="validator address (falls back to 'validator' in config file).",
    )(fn)


def contract_options(fn: Func) -> Func:
    """
    add the `--abi <contract_abi>` and `--address <contract_address>`
    options.
    """
    for option in reversed(
        [
            click.option(
                "--address",
                "contract_address_str",
                help="contract address (falls back to 'address' in config file).",
            ),
            click.option(
                "--abi",
                "contract_abi_path",
                type=Path(exists=True),
                help="contract ABI file (falls back to 'abi' in config file).",
            ),
        ]
    ):
        fn = option(fn)
    return fn
