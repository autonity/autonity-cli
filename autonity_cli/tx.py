"""
Transaction utility functions
"""

from typing import Callable, Optional

from eth_account.account import Account, SignedTransaction  # type: ignore
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3 import Web3
from web3._utils.transactions import fill_transaction_defaults
from web3.contract.contract import ContractFunction
from web3.types import Nonce, TxParams, TxReceipt, Wei

from .keyfile import (
    EncryptedKeyData,
    PrivateKey,
    decrypt_keyfile,
)


def create_transaction(
    from_addr: Optional[ChecksumAddress] = None,
    to_addr: Optional[ChecksumAddress] = None,
    value: Optional[Wei] = None,
    data: Optional[HexBytes] = None,
    gas: Optional[int] = None,
    gas_price: Optional[Wei] = None,
    max_fee_per_gas: Optional[Wei] = None,
    max_priority_fee_per_gas: Optional[Wei] = None,
    nonce: Optional[Nonce] = None,
    chain_id: Optional[int] = None,
) -> TxParams:
    """
    Optionally set some fields on a TxParams object.  This can then be
    passed to contract call methods, and then any remaining fields set
    with finalize_transaction.
    """
    tx: TxParams = {}

    if from_addr:
        tx["from"] = from_addr

    if to_addr:
        tx["to"] = to_addr

    if value:
        tx["value"] = value

    if data:
        tx["data"] = data

    if nonce is not None:
        tx["nonce"] = nonce

    if gas:
        tx["gas"] = gas

    if chain_id:
        tx["chainId"] = chain_id

    # Require either gas_price OR max_fee_per_gas, etc

    if gas_price:
        if max_fee_per_gas or max_priority_fee_per_gas:
            raise ValueError("gas price cannot be used with other fee parameters")
        tx["gasPrice"] = gas_price
    else:
        if max_fee_per_gas:
            tx["maxFeePerGas"] = max_fee_per_gas

            if max_priority_fee_per_gas:
                tx["maxPriorityFeePerGas"] = max_priority_fee_per_gas
            else:
                tx["maxPriorityFeePerGas"] = tx["maxFeePerGas"]

    return tx


def create_contract_function_transaction(
    function: ContractFunction,
    from_addr: ChecksumAddress,
    value: Optional[Wei] = None,
    gas: Optional[int] = None,
    gas_price: Optional[Wei] = None,
    max_fee_per_gas: Optional[Wei] = None,
    max_priority_fee_per_gas: Optional[Wei] = None,
    nonce: Optional[Nonce] = None,
    chain_id: Optional[int] = None,
) -> TxParams:
    """
    Given a contract call and other parameters, create an unsigned
    transaction (Web3 TxParams object).  Any fields not passed in will
    be filled out by querying the attached node, if available.
    """
    tx = create_transaction(
        from_addr=from_addr,
        value=value,
        gas=gas,
        gas_price=gas_price,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        nonce=nonce,
        chain_id=chain_id,
    )

    return function.build_transaction(tx)


def finalize_transaction(
    create_w3: Callable[[], Web3],
    tx: TxParams,
    from_addr: Optional[ChecksumAddress],
) -> TxParams:
    """
    Fill in any values not already set.  If necessary, a Web3 object
    will be created via the create_w3 callback.
    """

    w3: Optional[Web3] = None

    def get_web3() -> Web3:
        nonlocal w3
        if not w3:
            w3 = create_w3()
        return w3

    if "gas" not in tx:
        w3 = get_web3()
        tx["gas"] = w3.eth.estimate_gas(tx)

    if "nonce" not in tx:
        if not from_addr:
            raise ValueError("neither nonce or from-address given")
        w3 = get_web3()
        tx["nonce"] = w3.eth.get_transaction_count(from_addr)

    if "chainId" not in tx:
        w3 = get_web3()
        tx["chainId"] = w3.eth.chain_id

    if "gasPrice" not in tx and "maxFeePerGas" not in tx:
        tx = fill_transaction_defaults(get_web3(), tx)

    # The code above to fill defaults introduces an (unserializable)
    # empty bytes() in the "data" field.

    if "data" in tx:
        data = tx["data"]
        if len(data) == 0:
            del tx["data"]
        elif isinstance(data, bytes):
            tx["data"] = Web3.to_hex(data)

    return tx


def sign_tx_with_private_key(
    tx: TxParams, private_key: PrivateKey
) -> SignedTransaction:
    """
    For cases where the private key has already been decrypted.  (In
    general, for signing single transactions `sign_tx` is
    recommended.)
    """
    return Account.sign_transaction(tx, private_key)


def sign_tx(
    tx: TxParams, key_data: EncryptedKeyData, key_passphrase: str
) -> SignedTransaction:
    """
    Sign a transaction using the data from an encrypted keyfile and
    password.
    """
    private_key = decrypt_keyfile(key_data, key_passphrase)
    return sign_tx_with_private_key(tx, private_key)


def send_tx(w3: Web3, tx_signed: SignedTransaction) -> HexBytes:
    """
    Send raw signed tx bytes provided by 'tx_raw' to an RPC server
    to be validated and included in the blockchain.
    """
    raw_tx = tx_signed.raw_transaction
    tx_hash = w3.eth.send_raw_transaction(raw_tx)
    return tx_hash


def wait_for_tx(w3: Web3, tx_hash: HexBytes, timeout: Optional[float]) -> TxReceipt:
    """
    Wait for a specific transaction.  Returns the receipts.

    This simply wraps Web3.eth.wait_for_transaction_receipt, but uses
    stricter types (accepts only a HexBytes object).
    """
    if timeout is None:
        return w3.eth.wait_for_transaction_receipt(tx_hash)

    return w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
