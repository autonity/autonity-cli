# Copyright (C) 2015-2022 Clearmatics Technologies Ltd - All Rights Reserved.

"""
Keyfile utility functions
"""

import json
from typing import Any, Dict, NewType, cast

from eth_account import Account
from eth_keyfile import create_keyfile_json, decode_keyfile_json
from web3 import Web3
from web3.types import ChecksumAddress

EncryptedKeyData = Dict[str, Any]

PrivateKey = NewType("PrivateKey", bytes)


def load_keyfile(filename: str) -> EncryptedKeyData:
    """
    Load a keyfile.
    """
    with open(filename, "r", encoding="utf8") as keyfile_f:
        keyfile_json = json.load(keyfile_f)
        # TODO: validate the json
        return cast(EncryptedKeyData, keyfile_json)


def get_address_from_private_key(private_key: PrivateKey) -> ChecksumAddress:
    """
    Return the address associated with a given private key.
    """
    account = Account.from_key(private_key)  # pylint: disable=no-value-for-parameter
    return account.address


def create_keyfile_from_private_key(
    private_key: PrivateKey, password: str
) -> EncryptedKeyData:
    """
    Create a keyfile (with encrypted private key) from a private key.
    """
    assert len(private_key) == 32
    return create_keyfile_json(private_key, password.encode("utf8"))  # type: ignore


def get_address_from_keyfile(encrypted_key: EncryptedKeyData) -> ChecksumAddress:
    """
    Given some keyfile data, extract the address.
    """
    return Web3.to_checksum_address(encrypted_key["address"])


def decrypt_keyfile(encrypted_key: EncryptedKeyData, password: str) -> PrivateKey:
    """
    Decrypt the private key from a keyfile.
    """
    private_key = decode_keyfile_json(encrypted_key, password.encode("utf8"))  # type: ignore
    assert isinstance(private_key, bytes)
    return cast(PrivateKey, private_key)
