"""
Command line option sets used by multiple commands.
"""

from typing import Any, Callable, TypeVar

from click import Path, option

Func = TypeVar("Func", bound=Callable[..., Any])

Decorator = Callable[[Func], Func]


# an --rpc-endpoint, -r <url> option
rpc_endpoint_option = option(
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
        return option(
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
        fn = option(
            "--keyfile",
            "-k",
            required=required,
            type=Path(exists=not output),
            help="encrypted private key file (falls back to 'keyfile' in config file).",
        )(fn)
        return fn

    return decorator


def keyfile_and_password_options(required: bool = False) -> Decorator[Func]:
    """
    Options: --keyfile and --password.  If `required` is True,
    --keyfile is required.
    """

    def decorator(fn: Func) -> Func:
        fn = keyfile_option(required)(fn)
        fn = option(
            "--password",
            "-p",
            help="password for keyfile (falls back to KEYFILEPWD environment variable).",
        )(fn)
        return fn

    return decorator


def newton_or_token_option(fn: Func) -> Func:
    """
    Adds the --ntn and --token flags, allowing the user to specify
    that a transfer should use an ERC20 token.
    """
    fn = option("--ntn", is_flag=True, help="use Newton (NTN) as token")(fn)
    fn = option(
        "--token",
        "-t",
        metavar="TOKEN-ADDR",
        help="use the ERC20 token at the given address.",
    )(fn)
    return fn


def from_option(fn: Func) -> Func:
    """
    Adds the --from, -f option to specify the from field of a
    transaction.  Passed to the from_str parameter.
    """
    return option(
        "--from",
        "-f",
        "from_str",
        metavar="FROM",
        help="the sender address (extracted from keyfile if not given).",
    )(fn)


def tx_value_option(required: bool = False) -> Decorator[Func]:
    """
    Adds the --value, -v option to specify tx value field.  If `required` is True, the
    value must be provided.
    """

    def decorator(fn: Func) -> Func:
        fn = option(
            "--value",
            "-v",
            required=required,
            help=(
                "value in Auton or whole tokens "
                "(e.g. '0.000000007' and '7gwei' are identical)."
            ),
        )(fn)
        return fn

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
    fn = option(
        "--gas", "-g", help="maximum gas units that can be consumed by the tx."
    )(fn)
    fn = option(
        "--gas-price",
        "-p",
        help="value per gas in Auton (legacy, use -F and -P instead).",
    )(fn)
    fn = option(
        "--max-fee-per-gas",
        "-F",
        help="maximum to pay (in Auton) per gas for the total fee of the tx.",
    )(fn)
    fn = option(
        "--max-priority-fee-per-gas",
        "-P",
        help="maximum to pay (in Auton) per gas as tip to block proposer.",
    )(fn)
    fn = option(
        "--fee-factor",
        type=float,
        help="set maxFeePerGas to <last-basefee> x <fee-factor> [default: 2].",
    )(fn)
    fn = option(
        "--nonce",
        "-n",
        type=int,
        help="transaction nonce; query chain for account transaction count if not given.",
    )(fn)
    fn = option(
        "--chain-id",
        "-I",
        type=int,
        help="integer representing EIP155 chain ID.",
    )(fn)

    return fn


def validator_option(fn: Func) -> Func:
    """
    Add the --validator <address> option to specify a validator.  Uses
    the "validator_addr_str" argument.
    """
    return option(
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
    fn = option(
        "--address",
        "contract_address_str",
        help="contract address (falls back to 'address' in config file).",
    )(fn)
    fn = option(
        "--abi",
        "contract_abi_path",
        type=Path(exists=True),
        help="contract ABI file (falls back to 'abi' in config file).",
    )(fn)
    return fn
