"""Hardware wallet common functions.

Currently only Trezor devices are supported."""

import click
from trezorlib.client import TrezorClient, get_default_client
from trezorlib.transport import DeviceIsBusy


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
