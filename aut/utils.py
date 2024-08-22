"""
Utility functions that are only meant to be called by other functions in this package.
"""

import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Mapping, Optional, Sequence, TypeVar, Union, cast

from autonity import Autonity
from autonity.utils.keyfile import get_address_from_keyfile, load_keyfile
from autonity.utils.tx import (
    create_contract_function_transaction,
    create_transaction,
    finalize_transaction,
)
from eth_typing import ChecksumAddress
from click import ClickException
from hexbytes import HexBytes
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.types import BlockIdentifier, Nonce, TxParams, Wei

from .constants import AutonDenoms
from .logging import log

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals


# Intended to represent "value" types
V = TypeVar("V")


def from_address_from_argument_optional(
    from_addr: Optional[ChecksumAddress], keyfile: Optional[str]
) -> Optional[ChecksumAddress]:
    """
    Given an optional command line parameter, create an address,
    falling back to the keyfile given in the config.  May be null if
    neither is given.
    """

    if not from_addr:
        log("no from-addr given.  attempting to extract from keyfile")
        if keyfile:
            key_data = load_keyfile(keyfile)
            from_addr = get_address_from_keyfile(key_data)
            log(f"got keyfile: {keyfile}, address: {from_addr}")
        else:
            log("no keyfile.  empty from-addr")
            from_addr = None
    log(f"from_addr: {from_addr}")
    return from_addr


def from_address_from_argument(
    from_addr: Optional[ChecksumAddress], keyfile: Optional[str]
) -> ChecksumAddress:
    """
    Given an optional command line parameter, create an address,
    falling back to the keyfile given in the config.  Throws a
    ClickException if the address cannot be determined.
    """
    from_addr = from_address_from_argument_optional(from_addr, keyfile)
    if from_addr:
        return from_addr

    raise ClickException("From address or keyfile required")


def create_tx_from_args(
    w3: Web3,
    from_addr: Optional[ChecksumAddress] = None,
    to_addr: Optional[ChecksumAddress] = None,
    value: Optional[str] = None,
    data: Optional[HexBytes] = None,
    gas: Optional[int] = None,
    gas_price: Optional[Wei] = None,
    max_fee_per_gas: Optional[Wei] = None,
    max_priority_fee_per_gas: Optional[Wei] = None,
    fee_factor: Optional[float] = None,
    nonce: Optional[int] = None,
    chain_id: Optional[int] = None,
) -> TxParams:
    """
    Convenience function to setup a TxParams object based on optional
    command-line parameters.
    """

    if fee_factor:
        block_number = w3.eth.block_number
        block_data = w3.eth.get_block(block_number)
        max_fee_per_gas = Wei(int(float(block_data["baseFeePerGas"]) * fee_factor))

    try:
        return create_transaction(
            from_addr=from_addr,
            to_addr=to_addr,
            value=parse_wei_representation(value) if value else None,
            data=data,
            gas=cast(Wei, gas),
            gas_price=gas_price,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            nonce=cast(Nonce, nonce),
            chain_id=chain_id,
        )
    except ValueError as err:
        raise ClickException(err.args[0]) from err


def finalize_tx_from_args(
    w3: Web3,
    tx: TxParams,
    from_addr: Optional[ChecksumAddress],
) -> TxParams:
    """
    Fill in any values not set by create_tx_from_args.  Wraps the
    finalize_tx call in autonity.py.
    """
    return finalize_transaction(lambda: w3, tx, from_addr)


def create_contract_tx_from_args(
    function: ContractFunction,
    from_addr: ChecksumAddress,
    value: Optional[Wei] = None,
    gas: Optional[int] = None,
    gas_price: Optional[Wei] = None,
    max_fee_per_gas: Optional[Wei] = None,
    max_priority_fee_per_gas: Optional[Wei] = None,
    fee_factor: Optional[float] = None,
    nonce: Optional[int] = None,
    chain_id: Optional[int] = None,
) -> TxParams:
    """
    Convenience function to setup a TxParams object based on optional
    command-line parameters.  There is not need to call
    `finalize_tx_from_args` on the result of this function.
    """

    # TODO: abstract this calculation out

    if fee_factor:
        w3 = function.w3
        block_number = w3.eth.block_number
        block_data = w3.eth.get_block(block_number)
        max_fee_per_gas = Wei(
            int(Decimal(block_data["baseFeePerGas"]) * Decimal(fee_factor))
        )

    try:
        tx = create_contract_function_transaction(
            function=function,
            from_addr=from_addr,
            value=value,
            gas=cast(Wei, gas),
            gas_price=gas_price,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            nonce=cast(Nonce, nonce),
            chain_id=chain_id,
        )
        return finalize_transaction(lambda: function.w3, tx, from_addr)

    except ValueError as err:
        raise ClickException(err.args[0]) from err


def parse_wei_representation(wei_str: str) -> Wei:
    """
    Take a text representation of an integer with an optional
    denomination suffix (eg '2gwei' represents 2000000000
    wei). Returns an integer representing the value in wei.

    If no suffix is provided, it is assumed that the value
    is provided in whole tokens (ATN/NTN).
    """

    def _parse_numerical_part(numerical_part: str, denomination: int) -> int:
        return int(Decimal(numerical_part) * denomination)

    wei_str = wei_str.lower()
    try:
        if wei_str.endswith("kwei"):
            wei = _parse_numerical_part(wei_str[:-4], AutonDenoms.KWEI_VALUE_IN_WEI)
        elif wei_str.endswith("mwei"):
            wei = _parse_numerical_part(wei_str[:-4], AutonDenoms.MWEI_VALUE_IN_WEI)
        elif wei_str.endswith("gwei"):
            wei = _parse_numerical_part(wei_str[:-4], AutonDenoms.GWEI_VALUE_IN_WEI)
        elif wei_str.endswith("szabo"):
            wei = _parse_numerical_part(wei_str[:-5], AutonDenoms.SZABO_VALUE_IN_WEI)
        elif wei_str.endswith("finney"):
            wei = _parse_numerical_part(wei_str[:-6], AutonDenoms.FINNEY_VALUE_IN_WEI)
        elif wei_str.endswith("wei") or wei_str.endswith("attoton"):
            wei = _parse_numerical_part(wei_str[:-3], 1)
        else:
            wei = _parse_numerical_part(wei_str, AutonDenoms.AUTON_VALUE_IN_WEI)
    except Exception as exc:
        raise ValueError(
            f"{wei_str} is not a valid string representation of wei"
        ) from exc
    return Wei(wei)


def parse_token_value_representation(value_str: str, decimals: int) -> int:
    """
    Parse a token value (e.g. "0.001") into token units, given the
    number of decimals.  Suffices such as "wei" are not supported for
    tokens.
    """
    return int(Decimal(value_str) * Decimal(pow(10, decimals)))


def address_keyfile_dict(keystore_dir: str) -> Dict[ChecksumAddress, str]:
    """
    For directory 'keystore' that contains one or more keyfiles,
    return a dictionary with EIP55 checksum addresses as keys and
    keyfile path as value. If 'degenerate_addr', keys are addresses
    are all lower case and without the '0x' prefix.
    """
    addr_keyfile_dict: Dict[ChecksumAddress, str] = {}
    keyfile_list = os.listdir(keystore_dir)
    for fn in keyfile_list:
        keyfile_path = keystore_dir + "/" + fn
        try:
            keyfile = load_keyfile(keyfile_path)
        except json.JSONDecodeError:
            continue
        addr_lower = keyfile["address"]
        addr_keyfile_dict[Web3.to_checksum_address("0x" + addr_lower)] = keyfile_path

    return addr_keyfile_dict


def to_json(data: Union[Mapping[str, V], Sequence[V]], pretty: bool = False) -> str:
    """
    Take python data structure, return json formatted data.

    Note, the `Mapping[K, V]` type allows all `TypedDict` types
    (`TxParams`, `SignedTx`, etc) to be passed in.
    """
    if pretty:
        return json.dumps(cast(Dict[Any, Any], data), indent=2)

    return Web3.to_json(cast(Dict[Any, Any], data))


def string_is_32byte_hash(hash_str: str) -> bool:
    """
    Test if string is valid, 0x-prefixed representation of a
    32-byte hash. If it is, return True, otherwise return False.
    """
    if not hash_str.startswith("0x"):
        return False
    if not len(hash_str) == 66:  # 66-2 = 64 hex digits = 32 bytes
        return False
    try:
        int(hash_str, 16)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def validate_32byte_hash_string(hash_str: str) -> str:
    """
    If string represents a valid 32-byte hash, just return it,
    otherwise raise exception.
    """
    if not string_is_32byte_hash(hash_str):
        raise ValueError(f"{hash_str} is not a 32-byte hash")
    return hash_str


def validate_block_identifier(block_id: Union[str, int]) -> BlockIdentifier:
    """
    If string represents a valid block identifier, just return it,
    otherwise raise exception. A valid block identifier is either a
    32-byte hash or a positive integer representing the block
    number. Note that 'validity' here does not mean that the block
    exists, we're just testing that the _format_ of x is valid.
    """

    if isinstance(block_id, int):
        return block_id

    if isinstance(block_id, str):
        if block_id in ["latest", "earliest", "pending"]:
            return cast(BlockIdentifier, block_id)

        try:
            return int(block_id)
        except ValueError:
            pass

        return HexBytes(block_id)


def load_from_file_or_stdin(filename: str) -> str:
    """
    Open a file and return the stream, where '-' represents stdin.
    """

    if filename == "-":
        return sys.stdin.read()

    with open(filename, "r", encoding="utf8") as in_f:
        return in_f.read()


def load_from_file_or_stdin_line(filename: str) -> str:
    """
    Open a file and return the content. '-' means read a single line from stdin.
    """

    if filename == "-":
        return sys.stdin.readline()

    with open(filename, "r", encoding="utf8") as in_f:
        return in_f.read()


def newton_or_token_to_address(
    ntn: bool, token: Optional[ChecksumAddress]
) -> Optional[ChecksumAddress]:
    """
    Intended to be used in conjunction with the `newton_or_token`
    decorator which adds command line parameters.  Takes the parameter
    values and returns the address of the ERC20 contract to use.
    Doesn't instantiate the ERC20, since we may not have a Web3 object
    (and don't want to create one before validating all cli parameters.)
    """

    if ntn:
        if token:
            raise ClickException(
                "Cannot use --ntn and --token <addr> arguments together"
            )

        return Autonity.address()

    if token:
        return token

    return None


def newton_or_token_to_address_require(
    ntn: bool, token: Optional[ChecksumAddress]
) -> ChecksumAddress:
    """
    Similar to newton_or_token_address, but thrown an error if neither
    is given.
    """
    token = newton_or_token_to_address(ntn, token)
    if token is None:
        raise ClickException("Token address (or --ntn) must be specified.")

    return token


def geth_keyfile_name(key_time: datetime, address: ChecksumAddress) -> str:
    """
    Given a datetime and an address, construct the base of the file
    name of the keystore file, as used by geth.
    """
    # Convert the key_time into the correct format.
    keyfile_time = key_time.strftime("%Y-%m-%dT%H-%M-%S.%f000Z")
    # 0xca57....72EC -> ca57....72ec
    keyfile_address = address.lower()[2:]
    return f"UTC--{keyfile_time}--{keyfile_address}"


def new_keyfile_from_options(
    keystore: str, keyfile: Optional[str], keyfile_addr: ChecksumAddress
) -> str:
    """
    Logic to determine a (new) keyfile name, given keystore and
    keyfile options, where we fallback to filenames compatible with
    geth in the keystore.  Also checks for existence of the keyfile.
    """

    if keyfile is None:
        key_time = datetime.now(timezone.utc)
        if not os.path.exists(keystore):
            os.makedirs(keystore)
        keyfile = os.path.join(keystore, geth_keyfile_name(key_time, keyfile_addr))

    if os.path.exists(keyfile):
        raise ClickException(f"Refusing to overwrite existing keyfile {keyfile}")

    return keyfile


def parse_commission_rate(rate_str: str, rate_precision: int) -> int:
    """
    Support multiple rate formats and parse to a fixed-precision int
    argument.
    """

    # Handle ambiguous case
    if rate_str == "1" or rate_str.startswith("1.0"):
        raise ClickException(
            "Ambiguous rate. Use X%, 0.xx or a fixed-point value "
            f"(out of {rate_precision})"
        )

    if rate_str.endswith("%"):
        return int(Decimal(rate_precision) * Decimal(rate_str[:-1]) / Decimal(100))

    rate_dec = Decimal(rate_str)
    if rate_dec < Decimal(1):
        return int(Decimal(rate_precision) * rate_dec)

    try:
        rate_int = int(rate_str)
    except ValueError:
        raise ClickException(  # pylint: disable=raise-missing-from
            f"Expected integer instead of {rate_str}. See --help text"
        )

    return rate_int
