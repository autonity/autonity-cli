"""
Utility functions that are only meant to be called by other functions in this package.
"""

import json
import os
import re
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from getpass import getpass
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple, TypeVar, Union, cast

from autonity import Autonity
from autonity.constants import AUTONITY_CONTRACT_ADDRESS
from autonity.contracts import autonity
from click import ClickException
from eth_typing import ABI, ChecksumAddress
from hexbytes import HexBytes
from web3 import HTTPProvider, IPCProvider, LegacyWebSocketProvider, Web3
from web3._utils.encoding import Web3JsonEncoder
from web3.contract.contract import ContractFunction
from web3.providers import BaseProvider
from web3.types import (
    BlockIdentifier,
    Nonce,
    TxParams,
    Wei,
)

from . import config
from .constants import COMMISSION_RATE_PRECISION, AutonDenoms
from .denominations import NEWTON_DECIMALS
from .keyfile import load_keyfile
from .tx import (
    create_contract_function_transaction,
    create_transaction,
    finalize_transaction,
)

# Intended to represent "value" types
V = TypeVar("V")


class JSONEncoder(Web3JsonEncoder):
    def default(self, obj: Any) -> Any:
        if is_dataclass(obj):
            return asdict(obj)  # type: ignore
        return super().default(obj)


def web3_from_endpoint_arg(w3: Optional[Web3], endpoint_arg: Optional[str]) -> Web3:
    """
    Construct a Web3 from a cli argument.  CLI argument is not
    present, fall back to env vars and config files.

    Can also be used to implement the common pattern of initializing a
    Web3 "on-demand", for example to compute values only if they are
    not given on the command line, but ensure only one Web3 connection
    is created.

    See the `maketx` command which may or may not connect to a node to
    compute one or more of: gas parameters, nonce, chainID, etc.  If
    multiple of these must be computed, we should avoid creating
    multiple connections.  Conversely, if all of these values are
    given on the command line, no connected web3 object is required.
    """

    if w3 is None:
        return Web3(web3_provider_for_endpoint(config.get_rpc_endpoint(endpoint_arg)))
    return w3


def web3_provider_for_endpoint(endpoint: str) -> BaseProvider:
    """
    Given an rpc endpoint, return an appropriate provider (https, ws,
    or IPC). If identifier isn't a valid format of one of these three
    types, throws an exception.
    """
    regex_http = re.compile(r"^(?:http)s?://")
    if re.match(regex_http, endpoint) is not None:
        return HTTPProvider(endpoint)

    regex_ws = re.compile(r"^(?:ws)s?://")
    if re.match(regex_ws, endpoint) is not None:
        return LegacyWebSocketProvider(endpoint)

    regex_ipc = re.compile("([^ !$`&*()+]|(\\[ !$`&*()+]))+\\.ipc")
    if re.match(regex_ipc, endpoint) is not None:
        return IPCProvider(endpoint)

    raise ValueError(f"cannot determine provider for: {endpoint}")


def autonity_from_endpoint_arg(endpoint_arg: Optional[str]) -> autonity.Autonity:
    """
    Construct a reference to the Autonity contract from an endpoint
    argument.  Intended for the case of Protocol queries where the CLI
    function simply loads the Autonity contract and makes one request.
    """
    return Autonity(web3_from_endpoint_arg(None, endpoint_arg))


def create_tx_from_args(
    w3: Optional[Web3],
    rpc_endpoint: Optional[str],
    from_addr: Optional[ChecksumAddress] = None,
    to_addr: Optional[ChecksumAddress] = None,
    value: Optional[str] = None,
    data: Optional[str] = None,
    gas: Optional[str] = None,
    gas_price: Optional[str] = None,
    max_fee_per_gas: Optional[str] = None,
    max_priority_fee_per_gas: Optional[str] = None,
    fee_factor: Optional[float] = None,
    nonce: Optional[int] = None,
    chain_id: Optional[int] = None,
) -> Tuple[TxParams, Optional[Web3]]:
    """
    Convenience function to setup a TxParams object based on optional
    command-line parameters.
    """

    if fee_factor:
        w3 = web3_from_endpoint_arg(w3, rpc_endpoint)
        block_number = w3.eth.block_number
        block_data = w3.eth.get_block(block_number)
        if base_fee_per_gas := block_data.get("baseFeePerGas"):
            max_fee_per_gas = str(Wei(int(float(base_fee_per_gas) * fee_factor)))

    try:
        return (
            create_transaction(
                from_addr=from_addr,
                to_addr=to_addr,
                value=parse_wei_representation(value) if value else None,
                data=HexBytes(data) if data else None,
                gas=int(gas) if gas else None,
                gas_price=parse_wei_representation(gas_price) if gas_price else None,
                max_fee_per_gas=(
                    parse_wei_representation(max_fee_per_gas)
                    if max_fee_per_gas
                    else None
                ),
                max_priority_fee_per_gas=(
                    parse_wei_representation(max_priority_fee_per_gas)
                    if max_priority_fee_per_gas
                    else None
                ),
                nonce=Nonce(nonce) if nonce else None,
                chain_id=chain_id,
            ),
            w3,
        )
    except ValueError as err:
        raise ClickException(err.args[0]) from err


def finalize_tx_from_args(
    w3: Optional[Web3],
    rpc_endpoint: Optional[str],
    tx: TxParams,
    from_addr: Optional[ChecksumAddress],
) -> TxParams:
    """
    Fill in any values not set by create_tx_from_args.  Wraps the
    finalize_tx call in autonity.py.
    """

    def create_w3() -> Web3:
        return web3_from_endpoint_arg(w3, rpc_endpoint)

    return finalize_transaction(create_w3, tx, from_addr)


def create_contract_tx_from_args(
    function: ContractFunction,
    from_addr: ChecksumAddress,
    value: Optional[str] = None,
    gas: Optional[str] = None,
    gas_price: Optional[str] = None,
    max_fee_per_gas: Optional[str] = None,
    max_priority_fee_per_gas: Optional[str] = None,
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
        # Note, keep this in units of whole Auton.  It will be
        # converted to Wei below.
        if base_fee_per_gas := block_data.get("baseFeePerGas"):
            max_fee_per_gas = str(
                Decimal(base_fee_per_gas) * Decimal(fee_factor) / Decimal(pow(10, 18))
            )

    try:
        tx = create_contract_function_transaction(
            function=function,
            from_addr=from_addr,
            value=parse_wei_representation(value) if value else None,
            gas=int(gas) if gas else None,
            gas_price=parse_wei_representation(gas_price) if gas_price else None,
            max_fee_per_gas=(
                parse_wei_representation(max_fee_per_gas) if max_fee_per_gas else None
            ),
            max_priority_fee_per_gas=(
                parse_wei_representation(max_priority_fee_per_gas)
                if max_priority_fee_per_gas
                else None
            ),
            nonce=(Nonce(nonce) if nonce is not None) else None,
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

    If no suffix is provided, just coerce the string into an
    integer. If integer coercion fails, throw an exception.
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
        elif wei_str.endswith("auton"):
            wei = _parse_numerical_part(wei_str[:-5], AutonDenoms.AUTON_VALUE_IN_WEI)
        elif wei_str.endswith("aut"):
            wei = _parse_numerical_part(wei_str[:-3], AutonDenoms.AUTON_VALUE_IN_WEI)
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


def parse_newton_value_representation(newton_value_str: str) -> int:
    """
    Parse a value in NTN into Newton units.
    """
    return parse_token_value_representation(newton_value_str, NEWTON_DECIMALS)


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


def to_checksum_address(address: str) -> ChecksumAddress:
    """
    Take a blockchain address as string, convert the string into
    an EIP55 checksum address and return that.
    """
    checksum_address = Web3.to_checksum_address(address)
    return checksum_address


def to_json(data: Union[Mapping[str, V], Sequence[V]], pretty: bool = False) -> str:
    """
    Take python data structure, return json formatted data.

    Note, the `Mapping[K, V]` type allows all `TypedDict` types
    (`TxParams`, `SignedTx`, etc) to be passed in.
    """
    return json.dumps(
        cast(Dict[Any, Any], data), indent=(2 if pretty else None), cls=JSONEncoder
    )


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
    except Exception:
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
    ntn: bool, token: Optional[str]
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
                "cannot use --ntn and --token <addr> arguments together"
            )

        return AUTONITY_CONTRACT_ADDRESS

    if token:
        return Web3.to_checksum_address(token)

    return None


def newton_or_token_to_address_require(
    ntn: bool, token: Optional[str]
) -> ChecksumAddress:
    """
    Similar to newton_or_token_address, but thrown an error if neither
    is given.
    """
    token = newton_or_token_to_address(ntn, token)
    if token is None:
        raise ClickException("Token address (or --ntn) must be specified.")

    return token


def prompt_for_new_password() -> str:
    """
    Prompt for a new password (with confirmation), optionally echoing
    to the console.
    """
    prompt = "Password for new account: "
    prompt_2 = "Confirm account password: "
    password = getpass(prompt)
    password_2 = getpass(prompt_2)

    if password != password_2:
        raise ClickException("passwords do not match")

    return password


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
    keystore: Optional[str], keyfile: Optional[str], keyfile_addr: ChecksumAddress
) -> str:
    """
    Logic to determine a (new) keyfile name, given keystore and
    keyfile options, where we fallback to filenames compatible with
    geth in the keystore.  Also checks for existence of the keyfile.
    """

    if keyfile is None:
        key_time = datetime.now(timezone.utc)
        keystore = config.get_keystore_directory(keystore)
        if not os.path.exists(keystore):
            os.makedirs(keystore)
        keyfile = os.path.join(keystore, geth_keyfile_name(key_time, keyfile_addr))

    if os.path.exists(keyfile):
        raise ClickException(f"refusing to overwrite existing keyfile {keyfile}")

    return keyfile


def contract_address_and_abi_from_args(
    contract_address_str: Optional[str], contract_abi_path: Optional[str]
) -> Tuple[ChecksumAddress, ABI]:
    """
    Extract the address and ABI of a contract, given the command line
    args.  If arguments are not given, fall back to entries in the
    config file, otherwise raise an error.
    """

    contract_address = Web3.to_checksum_address(
        config.get_contract_address(contract_address_str)
    )
    contract_abi_path = config.get_contract_abi(contract_abi_path)
    contract_abi = _load_abi_file(contract_abi_path)
    return contract_address, contract_abi


def _load_abi_file(file_name: str) -> ABI:
    """
    Load an ABI from a file.
    """
    with open(file_name, "r", encoding="utf8") as abi_f:
        return json.load(abi_f)


def parse_commission_rate(rate_str: str) -> int:
    """
    Support multiple rate formats and parse to a fixed-precision int
    argument.
    """
    # Handle ambiguous case
    if rate_str == "1" or rate_str.startswith("1.0"):
        raise ClickException(
            "ambiguous rate. Use X%, 0.xx or a fixed-point value "
            f"(out of {COMMISSION_RATE_PRECISION}"
        )

    if rate_str.endswith("%"):
        return int(
            Decimal(COMMISSION_RATE_PRECISION) * Decimal(rate_str[:-1]) / Decimal(100)
        )

    rate_dec = Decimal(rate_str)
    if rate_dec < Decimal(1):
        return int(Decimal(COMMISSION_RATE_PRECISION) * rate_dec)

    try:
        rate_int = int(rate_str)
    except ValueError:
        raise ClickException(
            f"Expected integer instead of {rate_str}.  See --help text."
        )

    return rate_int
