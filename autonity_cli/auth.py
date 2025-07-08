import json
from typing import Optional, Protocol, cast

import click
from eth_account import Account
from eth_account.datastructures import SignedTransaction
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from eth_account.types import TransactionDictType
from eth_typing import ChecksumAddress
from web3.types import TxParams

from . import config
from .logging import log
from .utils import to_checksum_address


class Authenticator(Protocol):
    address: ChecksumAddress

    def sign_transaction(self, params: TxParams) -> SignedTransaction: ...

    def sign_message(self, message: str) -> bytes: ...


class KeyfileAuthenticator:
    def __init__(self, keyfile: str, password: Optional[str]):
        self.keyfile = keyfile
        self.password = password

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
            password = config.get_keyfile_password(self.password, self.keyfile)
            privkey = Account.decrypt(self.keydata, password=password)
            self._account = cast(LocalAccount, Account.from_key(privkey))
        return self._account

    def sign_transaction(self, params: TxParams) -> SignedTransaction:
        return self.account.sign_transaction(cast(TransactionDictType, params))

    def sign_message(self, message: str) -> bytes:
        signable = encode_defunct(text=message)
        return self.account.sign_message(signable)["signature"]


def get_authenticator(
    keyfile: Optional[str],
    password: Optional[str],
) -> Authenticator:
    keyfile = config.get_keyfile(keyfile)
    log(f"using key file: {keyfile}")
    return KeyfileAuthenticator(keyfile, password)
