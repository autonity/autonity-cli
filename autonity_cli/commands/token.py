from typing import Optional

from click import ClickException, argument, group
from web3 import Web3
from web3.exceptions import ContractLogicError

from ..denominations import format_quantity
from ..erc20 import ERC20
from ..options import (
    from_option,
    keyfile_option,
    newton_or_token_option,
    rpc_endpoint_option,
    tx_aux_options,
)
from ..utils import (
    create_contract_tx_from_args,
    from_address_from_argument,
    newton_or_token_to_address_require,
    parse_token_value_representation,
    to_json,
    web3_from_endpoint_arg,
)


@group(name="token")
def token_group() -> None:
    """
    Commands for working with ERC20 tokens.
    """


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
def name(rpc_endpoint: Optional[str], ntn: bool, token: Optional[str]) -> None:
    """
    The token's name (if available).
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)
    try:
        token_name = erc.name()
    except ContractLogicError as exc:
        raise ClickException(
            "Token does not implement the ERC20 `name` function"
        ) from exc
    print(token_name)


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
def symbol(rpc_endpoint: Optional[str], ntn: bool, token: Optional[str]) -> None:
    """
    The token's symbol (if available).
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)
    try:
        token_symbol = erc.symbol()
    except ContractLogicError as exc:
        raise ClickException(
            "Token does not implement the ERC20 `symbol` function"
        ) from exc
    print(token_symbol)


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
def decimals(rpc_endpoint: Optional[str], ntn: bool, token: Optional[str]) -> None:
    """
    The number of decimals used in the token balances.
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)
    print(erc.decimals())


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
def total_supply(rpc_endpoint: Optional[str], ntn: bool, token: Optional[str]) -> None:
    """
    Total supply (in units of whole Tokens).
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)
    token_decimals = erc.decimals()
    token_total_supply = erc.total_supply()
    print(format_quantity(token_total_supply, token_decimals))


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
@keyfile_option()
@argument("account_str", metavar="ACCOUNT", required=False)
def balance_of(
    rpc_endpoint: Optional[str],
    ntn: bool,
    token: Optional[str],
    keyfile: Optional[str],
    account_str: Optional[str],
) -> None:
    """
    The balance of ACCOUNT in tokens.

    If ACCOUNT is not specified, the default keyfile is used.
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    account_addr = from_address_from_argument(account_str, keyfile)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)
    balance = erc.balance_of(account_addr)
    token_decimals = erc.decimals()
    print(format_quantity(balance, token_decimals))


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
@keyfile_option()
@from_option
@argument("owner")
def allowance(
    rpc_endpoint: Optional[str],
    ntn: bool,
    token: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    owner: str,
) -> None:
    """
    The quantity of tokens that OWNER has granted the caller (`--from` address)
    permission to spend.
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    from_addr = from_address_from_argument(from_str, keyfile)
    owner_addr = Web3.to_checksum_address(owner)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)
    token_allowance = erc.allowance(owner_addr, from_addr)
    token_decimals = erc.decimals()
    print(format_quantity(token_allowance, token_decimals))


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
@keyfile_option()
@from_option
@tx_aux_options
@argument("recipient_str", metavar="RECIPIENT")
@argument("amount_str", metavar="AMOUNT")
def transfer(
    rpc_endpoint: Optional[str],
    ntn: bool,
    token: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    recipient_str: str,
    amount_str: str,
) -> None:
    """
    Create a transaction transferring AMOUNT of tokens to RECIPIENT.

    AMOUNT may be fractional if the token supports it.
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    from_addr = from_address_from_argument(from_str, keyfile)
    recipient_addr = Web3.to_checksum_address(recipient_str)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)

    token_decimals = erc.decimals()
    amount = parse_token_value_representation(amount_str, token_decimals)

    function_call = erc.transfer(recipient_addr, amount)
    tx = create_contract_tx_from_args(
        function=function_call,
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )

    print(to_json(tx))


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
@keyfile_option()
@from_option
@tx_aux_options
@argument("spender_str", metavar="SPENDER")
@argument("amount_str", metavar="AMOUNT")
def approve(
    rpc_endpoint: Optional[str],
    ntn: bool,
    token: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    spender_str: str,
    amount_str: str,
) -> None:
    """
    Create a transaction granting SPENDER permission to spend
    AMOUNT of tokens owned by the caller (`--from` address).

    AMOUNT may be fractional if the token supports it.
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    from_addr = from_address_from_argument(from_str, keyfile)
    spender = Web3.to_checksum_address(spender_str)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)

    token_decimals = erc.decimals()
    amount = parse_token_value_representation(amount_str, token_decimals)

    function_call = erc.approve(spender, amount)
    tx = create_contract_tx_from_args(
        function=function_call,
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )

    print(to_json(tx))


@token_group.command()
@rpc_endpoint_option
@newton_or_token_option
@keyfile_option()
@from_option
@tx_aux_options
@argument("spender_str", metavar="SPENDER")
@argument("recipient_str", metavar="RECIPIENT")
@argument("amount_str", metavar="AMOUNT")
def transfer_from(
    rpc_endpoint: Optional[str],
    ntn: bool,
    token: Optional[str],
    keyfile: Optional[str],
    from_str: Optional[str],
    gas: Optional[str],
    gas_price: Optional[str],
    max_priority_fee_per_gas: Optional[str],
    max_fee_per_gas: Optional[str],
    fee_factor: Optional[float],
    nonce: Optional[int],
    chain_id: Optional[int],
    spender_str: str,
    recipient_str: str,
    amount_str: str,
) -> None:
    """
    Create a transaction transferring AMOUNT of tokens held by SPENDER
    to RECIPIENT.

    SPENDER must previously have granted the caller
    (`--from` address) permission to spend these tokens, via an `approve`
    transaction. AMOUNT can be fractional if the token supports it.
    """

    token_addresss = newton_or_token_to_address_require(ntn, token)
    from_addr = from_address_from_argument(from_str, keyfile)
    spender = Web3.to_checksum_address(spender_str)
    recipient = Web3.to_checksum_address(recipient_str)

    w3 = web3_from_endpoint_arg(None, rpc_endpoint)
    erc = ERC20(w3, token_addresss)

    token_decimals = erc.decimals()
    amount = parse_token_value_representation(amount_str, token_decimals)

    function_call = erc.transfer_from(spender, recipient, amount)
    tx = create_contract_tx_from_args(
        function=function_call,
        from_addr=from_addr,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        fee_factor=fee_factor,
        nonce=nonce,
        chain_id=chain_id,
    )

    print(to_json(tx))
