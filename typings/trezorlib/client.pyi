from typing import Any, Optional

from trezorlib.messages import Features
from trezorlib.ui import TrezorClientUI

def get_default_client(
    path: Optional[str] = None, ui: Optional[TrezorClientUI] = None, **kwargs: Any
) -> TrezorClient: ...

class TrezorClient:
    features: Features
    ...
