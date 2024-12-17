"""ERC20 contract binding and data structures."""

import typing

import eth_typing
import web3
from web3.contract import contract


class ERC20:
    """ERC20 contract binding.

    Parameters
    ----------
    w3 : web3.Web3
    address : eth_typing.ChecksumAddress
        The address of a deployed ERC20 contract.
    """

    _contract: contract.Contract

    def __init__(
        self,
        w3: web3.Web3,
        address: eth_typing.ChecksumAddress,
    ):
        self._contract = w3.eth.contract(
            address=address,
            abi=ABI,
        )

    @property
    def Approval(self) -> contract.ContractEvent:
        """Binding for `event Approval` on the ERC20 contract."""
        return self._contract.events.Approval

    @property
    def Transfer(self) -> contract.ContractEvent:
        """Binding for `event Transfer` on the ERC20 contract."""
        return self._contract.events.Transfer

    def allowance(
        self,
        owner: eth_typing.ChecksumAddress,
        spender: eth_typing.ChecksumAddress,
    ) -> int:
        """Binding for `allowance` on the ERC20 contract.

        Parameters
        ----------
        owner : eth_typing.ChecksumAddress
        spender : eth_typing.ChecksumAddress

        Returns
        -------
        int
        """
        return_value = self._contract.functions.allowance(
            owner,
            spender,
        ).call()
        return int(return_value)

    def approve(
        self,
        spender: eth_typing.ChecksumAddress,
        value: int,
    ) -> contract.ContractFunction:
        """Binding for `approve` on the ERC20 contract.

        Parameters
        ----------
        spender : eth_typing.ChecksumAddress
        value : int

        Returns
        -------
        web3.contract.contract.ContractFunction
            A contract function instance to be sent in a transaction.
        """
        return self._contract.functions.approve(
            spender,
            value,
        )

    def balance_of(
        self,
        account: eth_typing.ChecksumAddress,
    ) -> int:
        """Binding for `balanceOf` on the ERC20 contract.

        Parameters
        ----------
        account : eth_typing.ChecksumAddress

        Returns
        -------
        int
        """
        return_value = self._contract.functions.balanceOf(
            account,
        ).call()
        return int(return_value)

    def decimals(
        self,
    ) -> int:
        """Binding for `decimals` on the ERC20 contract.

        Returns
        -------
        int
        """
        return_value = self._contract.functions.decimals().call()
        return int(return_value)

    def name(
        self,
    ) -> str:
        """Binding for `name` on the ERC20 contract.

        Returns
        -------
        str
        """
        return_value = self._contract.functions.name().call()
        return str(return_value)

    def symbol(
        self,
    ) -> str:
        """Binding for `symbol` on the ERC20 contract.

        Returns
        -------
        str
        """
        return_value = self._contract.functions.symbol().call()
        return str(return_value)

    def total_supply(
        self,
    ) -> int:
        """Binding for `totalSupply` on the ERC20 contract.

        Returns
        -------
        int
        """
        return_value = self._contract.functions.totalSupply().call()
        return int(return_value)

    def transfer(
        self,
        to: eth_typing.ChecksumAddress,
        value: int,
    ) -> contract.ContractFunction:
        """Binding for `transfer` on the ERC20 contract.

        Parameters
        ----------
        to : eth_typing.ChecksumAddress
        value : int

        Returns
        -------
        web3.contract.contract.ContractFunction
            A contract function instance to be sent in a transaction.
        """
        return self._contract.functions.transfer(
            to,
            value,
        )

    def transfer_from(
        self,
        from_: eth_typing.ChecksumAddress,
        to: eth_typing.ChecksumAddress,
        value: int,
    ) -> contract.ContractFunction:
        """Binding for `transferFrom` on the ERC20 contract.

        Parameters
        ----------
        from_ : eth_typing.ChecksumAddress
        to : eth_typing.ChecksumAddress
        value : int

        Returns
        -------
        web3.contract.contract.ContractFunction
            A contract function instance to be sent in a transaction.
        """
        return self._contract.functions.transferFrom(
            from_,
            to,
            value,
        )


ABI = typing.cast(
    eth_typing.ABI,
    [
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "allowance", "type": "uint256"},
                {"internalType": "uint256", "name": "needed", "type": "uint256"},
            ],
            "name": "ERC20InsufficientAllowance",
            "type": "error",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "sender", "type": "address"},
                {"internalType": "uint256", "name": "balance", "type": "uint256"},
                {"internalType": "uint256", "name": "needed", "type": "uint256"},
            ],
            "name": "ERC20InsufficientBalance",
            "type": "error",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "approver", "type": "address"}
            ],
            "name": "ERC20InvalidApprover",
            "type": "error",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "receiver", "type": "address"}
            ],
            "name": "ERC20InvalidReceiver",
            "type": "error",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "sender", "type": "address"}
            ],
            "name": "ERC20InvalidSender",
            "type": "error",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"}
            ],
            "name": "ERC20InvalidSpender",
            "type": "error",
        },
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "owner",
                    "type": "address",
                },
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "spender",
                    "type": "address",
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "value",
                    "type": "uint256",
                },
            ],
            "name": "Approval",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "from",
                    "type": "address",
                },
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "to",
                    "type": "address",
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "value",
                    "type": "uint256",
                },
            ],
            "name": "Transfer",
            "type": "event",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "owner", "type": "address"},
                {"internalType": "address", "name": "spender", "type": "address"},
            ],
            "name": "allowance",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "value", "type": "uint256"},
            ],
            "name": "approve",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "account", "type": "address"}
            ],
            "name": "balanceOf",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "decimals",
            "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "name",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "symbol",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "value", "type": "uint256"},
            ],
            "name": "transfer",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "from", "type": "address"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "value", "type": "uint256"},
            ],
            "name": "transferFrom",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
    ],
)
