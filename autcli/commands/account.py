"""
The `account` command group.
"""

from autcli.options import (
    keyfile_and_password_options,
    from_option,
    rpc_endpoint_option,
    newton_or_token_option,
    keyfile_option,
    keystore_option,
)
from click import group, command, option, argument, ClickException, Path
from typing import Dict, List, Optional

# Disable pylint warning about imports outside top-level.  We do this
# intentionally to try and keep startup times of the CLI low.

# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-locals


@group(name="account")
def account_group() -> None:
    """
    Commands related to specific accounts.
    """


@command(name="list")
@option("--with-files", is_flag=True, help="also show keyfile names.")
@keystore_option()
def list_cmd(keystore: Optional[str], with_files: bool) -> None:
    """
    List the accounts for files in the keystore directory.
    """

    from autcli import config
    from autcli.utils import address_keyfile_dict

    keystore = config.get_keystore_directory(keystore)
    keyfiles = address_keyfile_dict(keystore)
    for addr, keyfile in keyfiles.items():
        if with_files:
            print(addr + " " + keyfile)
        else:
            print(addr)


account_group.add_command(list_cmd)


@command()
@rpc_endpoint_option
@keyfile_option()
@option(
    "--asof",
    help="state as of TAG, one of block number, 'latest', 'earliest', or 'pending'.",
)
@argument("accounts", nargs=-1)
def info(
    rpc_endpoint: Optional[str],
    keyfile: Optional[str],
    accounts: List[str],
    asof: Optional[str],
) -> None:
    """
    Print some information about the given account (falling back to
    the default keyfile account if no accounts specified).
    """

    from autcli.user import get_account_stats
    from autcli.utils import (
        to_json,
        web3_from_endpoint_arg,
        from_address_from_argument_optional,
    )

    from web3 import Web3

    if len(accounts) == 0:
        account = from_address_from_argument_optional(None, keyfile)
        if not account:
            raise ClickException("No accounts specified")
        accounts = [account]

    addresses = [Web3.toChecksumAddress(act) for act in accounts]

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    account_stats = get_account_stats(w3, addresses, asof)
    print(to_json(account_stats, pretty=True))


account_group.add_command(info)


@command()
@rpc_endpoint_option
@newton_or_token_option
@keyfile_option()
@argument("account_str", metavar="ACCOUNT", default="")
def balance(
    rpc_endpoint: Optional[str],
    account_str: Optional[str],
    keyfile: Optional[str],
    ntn: bool,
    token: Optional[str],
) -> None:
    """
    Print the current balance of the given account.
    """

    from autcli.utils import (
        web3_from_endpoint_arg,
        newton_or_token_to_address,
        from_address_from_argument_optional,
    )

    from autonity import Autonity
    from autonity.erc20 import ERC20
    from autonity.utils.denominations import (
        format_quantity,
        format_auton_quantity,
        format_newton_quantity,
    )

    account_addr = from_address_from_argument_optional(account_str, keyfile)
    if not account_addr:
        raise ClickException(
            "could not determine account address from argument or keyfile"
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


account_group.add_command(balance)


@command()
@rpc_endpoint_option
@keyfile_option()
@argument("account_str", metavar="ACCOUNT", default="")
def lntn_balances(
    rpc_endpoint: Optional[str], account_str: Optional[str], keyfile: Optional[str]
) -> None:
    """
    Print the current balance of the given account.
    """

    from autcli.logging import log
    from autcli.utils import (
        to_json,
        web3_from_endpoint_arg,
        from_address_from_argument_optional,
    )

    from autonity.autonity import Autonity
    from autonity.erc20 import ERC20
    from autonity.utils.denominations import format_newton_quantity

    account_addr = from_address_from_argument_optional(account_str, keyfile)
    if not account_addr:
        raise ClickException(
            "could not determine account address from argument or keyfile"
        )

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    aut = Autonity(w3)
    validator_addrs = aut.get_validators()
    validators = [aut.get_validator(vaddr) for vaddr in validator_addrs]

    balances: Dict[str, str] = {}
    for validator in validators:
        log("computing holdings for validators {validator['addr']}")
        lnew = ERC20(w3, validator["liquid_contract"])
        bal = lnew.balance_of(account_addr)
        if bal:
            balances[validator["addr"]] = format_newton_quantity(bal)

    print(to_json(balances, pretty=True))


account_group.add_command(lntn_balances)


@command()
@keystore_option()
@keyfile_option(required=False, output=True)
@option(
    "--extra-entropy",
    type=Path(),
    help="File containing extra entropy.  Use '-' to prompt for keyboard input.",
)
@option(
    "--show-password",
    is_flag=True,
    help="Echo password input to the terminal",
)
def new(
    keystore: Optional[str],
    keyfile: Optional[str],
    extra_entropy: Optional[str],
    show_password: bool,
) -> None:
    """
    Create a new key and write it to a keyfile.
    """

    from autcli.logging import log
    from autcli.utils import prompt_for_new_password, new_keyfile_from_options

    from autonity.utils.keyfile import (
        create_keyfile_from_private_key,
        get_address_from_keyfile,
    )

    import json
    import eth_account

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

    password = prompt_for_new_password(show_password)
    log("Generating private key ...")
    account = eth_account.Account.create(entropy)
    keyfile_data = create_keyfile_from_private_key(account.key, password)
    keyfile_addr = get_address_from_keyfile(keyfile_data)
    if account.address != keyfile_addr:
        raise ClickException(
            f"internal error (address-mismatch) {account.address} != {keyfile_addr}"
        )

    # If keyfile was not given, generate a new keyfile based on
    # keystore and the new key details.
    keyfile = new_keyfile_from_options(keystore, keyfile, keyfile_addr)
    with open(keyfile, "w", encoding="utf8") as key_f:
        json.dump(keyfile_data, key_f)

    log(f"Encrypted key written to {keyfile}")

    print(keyfile_addr)


account_group.add_command(new)


@command()
@keyfile_option(required=True, output=True)
@option(
    "--show-password",
    is_flag=True,
    help="Echo password input to the terminal",
)
@argument("private_key_file", type=Path(exists=True))
def import_private_key(
    keyfile: str, show_password: bool, private_key_file: str
) -> None:
    """
    Read a plaintext private key file (as hex), and create a new
    encrypted keystore file for it.  Use - to read private key from
    stdin.
    """

    from autcli.utils import load_from_file_or_stdin, prompt_for_new_password
    from autcli.logging import log

    from autonity.utils.keyfile import (
        PrivateKey,
        create_keyfile_from_private_key,
        get_address_from_keyfile,
    )

    from hexbytes import HexBytes
    import json
    import os.path

    if os.path.exists(keyfile):
        raise ClickException("refusing to overwrite existing keyfile")

    private_key = HexBytes.fromhex(load_from_file_or_stdin(private_key_file))
    if len(private_key) != 32:
        raise ClickException("invalid private key length")

    password = prompt_for_new_password(show_password)

    keyfile_data = create_keyfile_from_private_key(PrivateKey(private_key), password)

    with open(keyfile, "w", encoding="utf8") as key_f:
        json.dump(keyfile_data, key_f)

    log(f"Encrypted key written to {keyfile}")

    print(get_address_from_keyfile(keyfile_data))


account_group.add_command(import_private_key)


@command()
@keyfile_and_password_options()
@argument(
    "tx-file",
    type=Path(),
    required=True,
)
def signtx(keyfile: Optional[str], password: Optional[str], tx_file: str) -> None:
    """
    Sign a transaction using the given keyfile.  Use '-' to read from
    stdin instead of a file.

    If password is not given, the env variable 'KEYFILEPWD' is used.
    If that is not set, the user is prompted.
    """

    from autcli.logging import log
    from autcli import config
    from autcli.utils import to_json, load_from_file_or_stdin

    from autonity.utils.tx import sign_tx

    import json

    # Read tx
    tx = json.loads(load_from_file_or_stdin(tx_file))

    # Read keyfile
    keyfile = config.get_keyfile(keyfile)
    log(f"using key file: {keyfile}")
    with open(keyfile, encoding="ascii") as key_f:
        encrypted_key = json.load(key_f)

    # Read password
    password = config.get_keyfile_password(password)

    # Sign the tx:
    signed_tx = sign_tx(tx, encrypted_key, password)

    print(to_json(signed_tx._asdict()))


account_group.add_command(signtx)


@command()
@keyfile_and_password_options()
@option(
    "--use-message-file",
    "-f",
    is_flag=True,
    help="Interpret MESSAGE as a filename where - means stdin",
)
@argument(
    "message",
    type=Path(),
)
@argument("signature-file", type=Path(), required=False)
def sign_message(
    keyfile: Optional[str],
    password: Optional[str],
    use_message_file: bool,
    message: str,
    signature_file: Optional[str],
) -> None:
    """
    Use the private key in the given keyfile to sign the string
    MESSAGE (or the contents of a file; see --use-message-file).  The
    signature is always written to stdout (which can be piped to a
    file). The signature is also written to SIGNATURE_FILE, if given.
    """

    from autcli.logging import log
    from autcli import config
    from autcli.utils import load_from_file_or_stdin

    from autonity.utils.keyfile import decrypt_keyfile

    from eth_account import Account
    from eth_account.messages import encode_defunct
    import json

    # Read message
    if use_message_file:
        message = load_from_file_or_stdin(message)

    # Read keyfile
    keyfile = config.get_keyfile(keyfile)
    log(f"using key file: {keyfile}")
    with open(keyfile, encoding="ascii") as key_f:
        encrypted_key = json.load(key_f)

    # Read password
    password = config.get_keyfile_password(password)
    private_key = decrypt_keyfile(encrypted_key, password)

    # Sign the message
    signature_data = Account().sign_message(
        signable_message=encode_defunct(text=message), private_key=private_key
    )
    signature = signature_data["signature"].hex()

    # Optionally write to the output file
    if signature_file:
        with open(signature_file, "w", encoding="ascii") as signature_f:
            signature_f.write(signature)

    print(signature)


account_group.add_command(sign_message)


@command()
@keyfile_option()
@from_option
@option(
    "--use-message-file",
    "-f",
    is_flag=True,
    help="Interpret MESSAGE as a filename where - means stdin",
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
    keyfile: Optional[str],
    from_str: Optional[str],
    use_message_file: bool,
    message: str,
    signature_file: str,
) -> None:

    """
    Verify that the signature in SIGNATURE_FILE` is valid for the
    message MESSAGE, signed by the owner of the FROM address.
    Signature must be contained in a file.
    """

    from autcli.logging import log
    from autcli.utils import (
        from_address_from_argument_optional,
        load_from_file_or_stdin,
    )

    from hexbytes import HexBytes
    from eth_account import Account
    from eth_account.messages import encode_defunct

    if use_message_file:
        message = load_from_file_or_stdin(message)

    with open(signature_file, "r", encoding="ascii") as signature_f:
        # TODO: check file size before blindly reading everything
        signature_hex = signature_f.read().rstrip()
        signature = HexBytes(signature_hex)

    from_addr = from_address_from_argument_optional(from_str, keyfile)

    recovered_addr = Account().recover_message(
        encode_defunct(text=message), signature=signature
    )

    if recovered_addr != from_addr:
        log(f"recovered address was {recovered_addr}, not {from_addr}")
        raise ClickException("Signature invalid")

    log("signature is valid")


account_group.add_command(verify_signature)
