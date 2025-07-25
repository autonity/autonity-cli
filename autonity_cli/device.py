"""Hardware device utility functions.

Currently only Trezor devices are supported."""

import click
import trezorlib.ethereum as trezor_eth
from eth_typing import ChecksumAddress
from trezorlib.client import TrezorClient, get_default_client
from trezorlib.exceptions import Cancelled
from trezorlib.tools import parse_path
from trezorlib.transport import DeviceIsBusy

from .utils import to_checksum_address

TREZOR_DEFAULT_PREFIX = "m/44h/60h/0h/0"


def get_client() -> TrezorClient:
    try:
        return get_default_client()
    except DeviceIsBusy as exc:
        raise click.ClickException("Device in use by another process.") from exc
    except Exception as exc:
        raise click.ClickException(
            "No Trezor device found. Check device is connected, unlocked, and detected by OS."
        ) from exc


def enumerate_accounts(
    prefix: str, start: int, n: int
) -> list[tuple[ChecksumAddress, str]]:
    accounts: list[tuple[ChecksumAddress, str]] = []
    client = get_client()
    try:
        for index in range(start, start + n):
            path_str = prefix + f"/{index}"
            try:
                path = parse_path(path_str)
            except ValueError as exc:
                raise click.ClickException(
                    f"Invalid Trezor BIP32 derivation path '{path_str}'."
                ) from exc
            address_str = trezor_eth.get_address(client, path)
            accounts.append((to_checksum_address(address_str), path_str))
    except Cancelled as exc:  # user cancelled optional passphrase prompt
        raise click.Abort() from exc
    return accounts
