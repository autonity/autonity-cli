import json
from typing import Optional, Protocol, cast

import click
import trezorlib.ethereum as trezor_eth
from eth_account import Account
from eth_account._utils.legacy_transactions import encode_transaction
from eth_account.datastructures import SignedTransaction
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from eth_account.typed_transactions.typed_transaction import TypedTransaction
from eth_account.types import TransactionDictType
from eth_typing import ChecksumAddress
from eth_utils.conversions import to_int
from eth_utils.crypto import keccak
from hexbytes import HexBytes
from trezorlib.exceptions import Cancelled
from trezorlib.messages import Features
from trezorlib.tools import parse_path
from web3.types import TxParams

from . import config, device
from .logging import log
from .utils import to_checksum_address

TREZOR_DEFAULT_PREFIX = "m/44h/60h/0h/0"


class Authenticator(Protocol):
    address: ChecksumAddress

    def sign_transaction(self, params: TxParams) -> SignedTransaction: ...

    def sign_message(self, message: str) -> bytes: ...


class KeyfileAuthenticator:
    def __init__(self, keyfile: str):
        self.keyfile = keyfile

        with click.open_file(self.keyfile, "rb") as kf:
            self.keydata = json.load(kf)
        keyfile_addr = self.keydata.get("address")
        if not keyfile_addr:
            raise RuntimeError("Unrecognized keyfile format.")
        self.address = to_checksum_address(keyfile_addr)
        self._account: LocalAccount | None = None

    @property
    def account(self) -> LocalAccount:
        if self._account is None:
            password = config.get_keyfile_password(None, self.keyfile)
            privkey = Account.decrypt(self.keydata, password=password)
            self._account = cast(LocalAccount, Account.from_key(privkey))
        return self._account

    def sign_transaction(self, params: TxParams) -> SignedTransaction:
        return self.account.sign_transaction(cast(TransactionDictType, params))

    def sign_message(self, message: str) -> bytes:
        signable = encode_defunct(text=message)
        return self.account.sign_message(signable)["signature"]


class TrezorAuthenticator:
    def __init__(self, path_or_index: str):
        if path_or_index.isdigit():
            path_str = f"{TREZOR_DEFAULT_PREFIX}/{int(path_or_index)}"
        else:
            path_str = path_or_index
        try:
            self.path = parse_path(path_str)
        except ValueError as exc:
            raise click.ClickException(
                f"Invalid Trezor BIP32 derivation path '{path_str}'."
            ) from exc
        self.client = device.get_client()
        device_info = self.device_info(self.client.features)
        log(f"Connected to Trezor: {device_info}")

        try:
            address_str = trezor_eth.get_address(self.client, self.path)
        except Cancelled as exc:
            raise click.Abort() from exc

        self.address = to_checksum_address(address_str)
        self.path_str = path_str

    def device_info(self, features: Features) -> str:
        model = str(features.model) or "1"
        label = features.label or "(none)"
        return f"model='{model}', device_id='{features.device_id}', label='{label}'"

    def sign_transaction(self, params: "TxParams") -> SignedTransaction:
        assert "chainId" in params
        assert "gas" in params
        assert "maxFeePerGas" in params
        assert "maxPriorityFeePerGas" in params
        assert "nonce" in params
        assert "to" in params
        assert "value" in params
        v_int, r_bytes, s_bytes = trezor_eth.sign_tx_eip1559(
            self.client,
            self.path,
            nonce=params["nonce"],
            gas_limit=params["gas"],
            to=str(params["to"]),
            value=params["value"],
            data=HexBytes(params["data"]) if "data" in params else HexBytes(b""),
            chain_id=params["chainId"],
            max_gas_fee=int(params["maxFeePerGas"]),
            max_priority_fee=int(params["maxPriorityFeePerGas"]),
        )
        r_int = to_int(r_bytes)
        s_int = to_int(s_bytes)
        filtered_params = dict((k, v) for (k, v) in params.items() if k != "from")
        tx_unsigned = TypedTransaction.from_dict(
            cast(TransactionDictType, filtered_params)
        )
        tx_encoded = encode_transaction(tx_unsigned, vrs=(v_int, r_int, s_int))
        txhash = keccak(tx_encoded)
        return SignedTransaction(
            raw_transaction=HexBytes(tx_encoded),
            hash=HexBytes(txhash),
            r=r_int,
            s=s_int,
            v=v_int,
        )

    def sign_message(self, message: str) -> bytes:
        sigdata = trezor_eth.sign_message(
            self.client,
            self.path,
            message,
        )
        return sigdata.signature


def validate_authenticator(
    *, keyfile: Optional[str], trezor: Optional[str]
) -> Authenticator:
    if trezor and keyfile:
        raise RuntimeError("Expected at most one authentication method.")
    elif trezor:
        log(f"using Trezor: {trezor}")
        return TrezorAuthenticator(trezor)
    else:
        log(f"using key file: {keyfile}")
        keyfile = config.get_keyfile(keyfile)
        return KeyfileAuthenticator(keyfile)


def validate_authenticator_account(
    address: Optional[str],
    keyfile: Optional[str],
    trezor: Optional[str],
) -> ChecksumAddress:
    """Validate an account address.

    If the `address_str` is provided, return that, otherwise look up the address
    with the authenticator returned by `validate_authenticator`.
    """
    if address:
        _address = to_checksum_address(address)
    else:
        log("No address provided, using an authenticator")
        auth = validate_authenticator(keyfile=keyfile, trezor=trezor)
        _address = auth.address
    log(f"address: {_address}")
    return _address
