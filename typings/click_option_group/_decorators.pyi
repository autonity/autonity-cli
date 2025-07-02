from typing import Any, Callable, Optional, Type

from click.decorators import FC
from click_option_group._core import OptionGroup

class _OptGroup:
    def group(
        self,
        name: Optional[str] = None,
        *,
        help: Optional[str] = None,
        cls: Optional[Type[OptionGroup]] = None,
        **attrs: Any,
    ) -> Callable[[FC], FC]: ...
    def option(self, *param_decls: str, **attrs: Any) -> Callable[[FC], FC]: ...

optgroup: _OptGroup
