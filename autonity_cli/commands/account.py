import getpass
import json
from typing import List, Optional

import click
import eth_account
from autonity import Autonity
from click import ClickException, Path, argument, group, option
from eth_account import Account
from eth_account.messages import encode_defunct
from hexbytes import HexBytes
from web3 import Web3
from web3.types import BlockIdentifier

from .. import config, device
from ..auth import (
    TREZOR_DEFAULT_PREFIX,
    validate_authenticator,
    validate_authenticator_account,
)
from ..denominations import (
    format_auton_quantity,
    format_newton_quantity,
    format_quantity,
)
from ..erc20 import ERC20
from ..keyfile import (
    PrivateKey,
    create_keyfile_from_private_key,
    get_address_from_keyfile,
)
from ..logging import log
from ..options import (
    authentication_options,
    from_options,
    keyfile_option,
    keystore_option,
    newton_or_token_option,
    optgroup,
    rpc_endpoint_option,
)
from ..user import get_account_stats
from ..utils import (
    address_keyfile_dict,
    load_from_file_or_stdin,
    load_from_file_or_stdin_line,
    new_keyfile_from_options,
    newton_or_token_to_address,
    prompt_for_new_password,
    to_json,
    web3_from_endpoint_arg,
)


@group(name="account")
def account_group() -> None:
    """
    Commands related to specific accounts.
    """


@account_group.command(name="list")
@optgroup.group("Keyfile accounts")
@keystore_option(cls=optgroup.option)
@optgroup.group("Trezor accounts")
@optgroup.option(
    "--trezor", "use_trezor", is_flag=True, help="Enumerate Trezor accounts"
)
@optgroup.option(
    "--prefix",
    metavar="PREFIX",
    default=TREZOR_DEFAULT_PREFIX,
    show_default=True,
    help="Custom BIP32 derivation prefix",
)
@optgroup.option(
    "--start",
    type=int,
    default=0,
    show_default=True,
    help="Start index at BIP32 derivation prefix",
)
@optgroup.option(
    "-n",
    type=int,
    default=20,
    show_default=True,
    help="Number of Trezor accounts to list",
)
def list_cmd(
    keystore: Optional[str], use_trezor: bool, prefix: str, start: int, n: int
) -> None:
    """
    List accounts in keyfiles or in a Trezor device.
    """

    if use_trezor and keystore:
        raise click.ClickException(
            "Options --trezor and --keystore are mutually exclusive."
        )

    if use_trezor:
        accounts = device.enumerate_accounts(prefix, start, n)
    else:
        keystore = config.get_keystore_directory(keystore)
        accounts = address_keyfile_dict(keystore).items()
    for addr, path in accounts:
        print(addr + " " + path)


@account_group.command()
@rpc_endpoint_option
@authentication_options()
@option(
    "--asof",
    help="state as of TAG, one of block number, 'latest', 'earliest', or 'pending'.",
)
@argument("accounts", nargs=-1)
def info(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    accounts: List[str],
    asof: Optional[BlockIdentifier],
) -> None:
    """
    Print information about the given account.

    Falls back to the default keyfile if no account is specified.
    """

    if len(accounts) == 0:
        auth = validate_authenticator(keyfile=keyfile, trezor=trezor)
        accounts = [auth.address]

    addresses = [Web3.to_checksum_address(act) for act in accounts]

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    account_stats = get_account_stats(w3, addresses, asof)
    print(to_json(account_stats, pretty=True))


@account_group.command()
@rpc_endpoint_option
@newton_or_token_option
@authentication_options()
@argument("account_str", metavar="ACCOUNT", default="")
def balance(
    rpc_endpoint: Optional[str],
    account_str: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    ntn: bool,
    token: Optional[str],
) -> None:
    """
    Print the current balance of the given account.
    """

    account_addr = validate_authenticator_account(
        account_str, keyfile=keyfile, trezor=trezor
    )

    token_addresss = newton_or_token_to_address(ntn, token)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)

    # TODO: support printing in other denominations (AUT / units based
    # on num decimals of token).

    if ntn:
        autonity = Autonity(w3)
        print(format_newton_quantity(autonity.balance_of(account_addr)))

    elif token_addresss is not None:
        token_contract = ERC20(w3, token_addresss)
        decimals = token_contract.decimals()
        bal = token_contract.balance_of(account_addr)
        print(format_quantity(bal, decimals))

    else:
        print(format_auton_quantity(w3.eth.get_balance(account_addr)))


@account_group.command()
@keystore_option()
@keyfile_option(output=True)
@option(
    "--extra-entropy",
    type=Path(),
    help="file containing extra entropy. Use '-' to prompt for keyboard input.",
)
def new(
    keystore: Optional[str],
    keyfile: Optional[str],
    extra_entropy: Optional[str],
) -> None:
    """
    Create a new key and write it to a keyfile.

    If no keyfile is specified, a default name is used (consistent with GETH keyfiles)
    in the keystore.
    """

    # Ask for extra entropy, if requested.

    entropy: str = ""
    if extra_entropy:
        if extra_entropy == "-":
            entropy = input("Random string (press ENTER to finish): ")
        else:
            # Use ascii so that binary data is not reinterpreted.
            with open(extra_entropy, "r", encoding="ascii") as entropy_f:
                entropy = entropy_f.read()

    # Ask for password (and confirmation) and ensure both entries
    # match.

    password = prompt_for_new_password()
    log("Generating private key ...")
    account = eth_account.Account.create(entropy)
    keyfile_data = create_keyfile_from_private_key(account.key, password)
    keyfile_addr = get_address_from_keyfile(keyfile_data)
    if account.address != keyfile_addr:
        raise ClickException(
            f"Internal error (address-mismatch) {account.address} != {keyfile_addr}"
        )

    # If keyfile was not given, generate a new keyfile based on
    # keystore and the new key details.
    keyfile = new_keyfile_from_options(keystore, keyfile, keyfile_addr)
    with open(keyfile, "w", encoding="utf8") as key_f:
        json.dump(keyfile_data, key_f)

    log(f"Encrypted key written to {keyfile}")

    print(f"{keyfile_addr}  {keyfile}")


@account_group.command()
@keystore_option()
@keyfile_option(output=True)
@argument("private_key_file", type=Path(exists=False))
def import_private_key(
    keystore: Optional[str],
    keyfile: Optional[str],
    private_key_file: str,
) -> None:
    """
    Read a plaintext private key file (as hex-string), and create a new encrypted
    keystore file for it.

    Use '-' to read private key from standard input. If no keyfile is specified,
    a default name is used (consistent with GETH keyfiles) in the keystore.
    """

    private_key = HexBytes.fromhex(load_from_file_or_stdin_line(private_key_file))
    if len(private_key) != 32:
        raise ClickException("Invalid private key length")

    password = prompt_for_new_password()

    keyfile_data = create_keyfile_from_private_key(PrivateKey(private_key), password)
    keyfile_addr = get_address_from_keyfile(keyfile_data)

    keyfile = new_keyfile_from_options(keystore, keyfile, keyfile_addr)
    with open(keyfile, "w", encoding="utf8") as key_f:
        json.dump(keyfile_data, key_f)

    log(f"Encrypted key written to {keyfile}")

    keyfile_addr = get_address_from_keyfile(keyfile_data)
    print(f"{keyfile_addr}  {keyfile}")


@account_group.command()
@argument("keyfile-path", required=False, type=Path(exists=True))
def reveal_private_key(
    keyfile_path: Optional[str],
) -> None:
    """
    Print the private key from the specified keyfile to standard output in hex-string
    format.

    The keyfile path is taken from the config file if not specified.
    """

    confirmation = input(
        "⚠️ WARNING! This command exposes an account's private key.\n"
        "Type 'yes' to continue: "
    )
    if confirmation.lower() != "yes":
        raise ClickException("Interrupted")

    password = getpass.getpass("Keyfile password: ")

    with open(config.get_keyfile(keyfile_path), encoding="utf-8") as f:
        encrypted_key = f.read()

    try:
        key = Web3().eth.account.decrypt(encrypted_key, password)
    except ValueError as e:
        raise ClickException(str(e))

    print(Web3.to_hex(key))


@account_group.command()
@authentication_options()
@argument(
    "tx-file",
    type=Path(),
    required=True,
)
def signtx(keyfile: Optional[str], trezor: Optional[str], tx_file: str) -> None:
    """
    Sign a transaction using the given keyfile.

    Use '-' to read from standard input instead of a file.

    If the environment variable 'KEYFILEPWD' is set, this keyfile password will
    be used used. If this is not set, the user is prompted.
    """

    # Read tx
    tx = json.loads(load_from_file_or_stdin(tx_file))

    # Get auth
    auth = validate_authenticator(keyfile=keyfile, trezor=trezor)

    # Check for mismatch
    if "from" in tx and tx["from"] != auth.address:
        raise ClickException(
            f"TX from-address {tx['from']} does not match signer's address {auth.address}."
        )

    # Sign the tx:
    signed_tx = auth.sign_transaction(tx)

    print(to_json(signed_tx._asdict()))


@account_group.command()
@authentication_options()
@option(
    "--use-message-file",
    "-f",
    is_flag=True,
    help="interpret MESSAGE as a filename where '-' means standard input.",
)
@argument(
    "message",
    type=Path(),
)
@argument("signature-file", type=Path(), required=False)
def sign_message(
    keyfile: Optional[str],
    trezor: Optional[str],
    use_message_file: bool,
    message: str,
    signature_file: Optional[str],
) -> None:
    """
    Use the private key in the given keyfile to sign the string
    MESSAGE (or the contents of a file; see --use-message-file).

    The signature is always written to standard output (which can be piped to a
    file). The signature is also written to SIGNATURE_FILE, if given.
    """

    # Read message
    if use_message_file:
        message = load_from_file_or_stdin(message)

    # Get auth
    auth = validate_authenticator(keyfile=keyfile, trezor=trezor)

    # Sign the message
    log(f'Signing message: "{message}" (len={len(message)})')
    signature = auth.sign_message(message).hex()

    # Optionally write to the output file
    if signature_file:
        with open(signature_file, "w", encoding="ascii") as signature_f:
            signature_f.write(signature)

    print(signature)


@account_group.command()
@from_options()
@option(
    "--use-message-file",
    "-m",
    is_flag=True,
    help="interpret MESSAGE as a filename where '-' means standard input.",
)
@argument(
    "message",
    type=Path(),
    required=True,
)
@argument(
    "signature-file",
    type=Path(),
    required=True,
)
def verify_signature(
    from_str: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
    use_message_file: bool,
    message: str,
    signature_file: str,
) -> None:
    """
    Verify that the signature in `SIGNATURE_FILE` is valid for the
    message MESSAGE, signed by the owner of the FROM address.

    Signature must be contained in a file.
    """

    if use_message_file:
        message = load_from_file_or_stdin(message)

    with open(signature_file, "r", encoding="ascii") as signature_f:
        # TODO: check file size before blindly reading everything
        signature_hex = signature_f.read().rstrip()
        signature = HexBytes(signature_hex)

    from_addr = validate_authenticator_account(from_str, keyfile=keyfile, trezor=trezor)

    recovered_addr = Account().recover_message(
        encode_defunct(text=message), signature=signature
    )

    if recovered_addr != from_addr:
        log(f"recovered address was {recovered_addr}, not {from_addr}")
        raise ClickException("Signature invalid")

    log("signature is valid")
