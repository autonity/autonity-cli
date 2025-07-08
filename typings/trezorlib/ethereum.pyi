from typing import AnyStr, List, Optional, Tuple

from trezorlib import messages
from trezorlib.tools import Address

from .client import TrezorClient

def get_address(
    client: TrezorClient,
    n: Address,
    show_display: bool = False,
    encoded_network: Optional[bytes] = None,
    chunkify: bool = False,
) -> str: ...
def sign_tx_eip1559(
    client: TrezorClient,
    n: Address,
    *,
    nonce: int,
    gas_limit: int,
    to: str,
    value: int,
    data: bytes = b"",
    chain_id: int,
    max_gas_fee: int,
    max_priority_fee: int,
    access_list: Optional[List[messages.EthereumAccessList]] = None,
    definitions: Optional[messages.EthereumDefinitions] = None,
    chunkify: bool = False,
) -> Tuple[int, bytes, bytes]: ...
def sign_message(
    client: TrezorClient,
    n: Address,
    message: AnyStr,
    encoded_network: Optional[bytes] = None,
    chunkify: bool = False,
) -> messages.EthereumMessageSignature: ...
