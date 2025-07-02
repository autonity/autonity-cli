"""
Configuration-related code.  Determines precedence of command
line, config and defaults, and handles extracting from the config
file.
"""

import os
import os.path
from getpass import getpass
from typing import Optional

from click import ClickException
from eth_typing import ChecksumAddress
from web3 import Web3

from .config_file import CONFIG_FILE_NAME, get_config_file
from .logging import log

DEFAULT_KEYFILE_DIRECTORY = "~/.autonity/keystore"
KEYFILE_DIRECTORY_ENV_VAR = "KEYFILEDIR"
KEYFILE_ENV_VAR = "KEYFILE"
KEYFILE_PASSWORD_ENV_VAR = "KEYFILEPWD"
WEB3_ENDPOINT_ENV_VAR = "WEB3_ENDPOINT"
CONTRACT_ADDRESS_ENV_VAR = "CONTRACT_ADDRESS"
CONTRACT_ABI_ENV_VAR = "CONTRACT_ABI"


def get_keystore_directory(keystore_directory: Optional[str]) -> str:
    """
    Get the keystore directory.  In order, use the command-line
    parameter, falling back to the env var then config file, and finally to
    DEFAULT_KEYFILE_DIRECTORY.
    """
    if keystore_directory is None:
        keystore_directory = os.getenv(KEYFILE_DIRECTORY_ENV_VAR)
        if keystore_directory is None:
            keystore_directory = get_config_file().get_path("keystore")
            if keystore_directory is None:
                keystore_directory = os.path.expanduser(DEFAULT_KEYFILE_DIRECTORY)

    assert keystore_directory is not None
    return keystore_directory


def get_keyfile_optional(keyfile: Optional[str]) -> Optional[str]:
    """
    Get the keyfile configuration if available.
    """
    if keyfile is None:
        keyfile = os.getenv(KEYFILE_ENV_VAR)
        if keyfile is None:
            keyfile = get_config_file().get_path("keyfile")

    return keyfile


def get_keyfile(keyfile: Optional[str]) -> str:
    """
    Get the keyfile configuration, raising a Click error if not given.
    """
    keyfile = get_keyfile_optional(keyfile)
    if keyfile is None:
        raise ClickException(
            f"No keyfile specified (use --keyfile, {KEYFILE_ENV_VAR} env var "
            f"or {CONFIG_FILE_NAME})"
        )

    return keyfile


def get_keyfile_password(password: Optional[str], keyfile: Optional[str] = None) -> str:
    """
    Get the keyfile password, given a cli parameter `password`.  Fall
    back to env vars if cli parameter is not given, then to user
    input.
    """

    # Read password
    if password is None:
        password = os.getenv(KEYFILE_PASSWORD_ENV_VAR)
        if password is None:
            password = getpass(
                f"(consider using '{KEYFILE_PASSWORD_ENV_VAR}' env var).\n"
                + "Enter passphrase "
                + ("" if keyfile is None else f"for {keyfile} ")
                + "(or CTRL-d to exit): "
            )

    return password


def get_rpc_endpoint(endpoint: Optional[str]) -> str:
    """
    Get the RPC endpoint configuration value, where param is the
    command-line option. If param is not given, check the env var,
    then configuration files, falling back to the default.
    """

    if endpoint is None:
        endpoint = os.getenv(WEB3_ENDPOINT_ENV_VAR)
        if endpoint is None:
            endpoint = get_config_file().get("rpc_endpoint")
            if endpoint is None:
                raise ClickException(
                    f"No RPC endpoint given (use --rpc-endpoint, {WEB3_ENDPOINT_ENV_VAR} "
                    f"env var or {CONFIG_FILE_NAME})"
                )

            log(f"endpoint from config file: {endpoint}")
        else:
            log(f"endpoint from env var: {endpoint}")
    else:
        log(f"endpoint from command line: {endpoint}")

    return endpoint


def get_node_address(validator_addr_str: Optional[str]) -> ChecksumAddress:
    """
    Validator address to use, cli parameter falling back to any config file.
    """

    if not validator_addr_str:
        validator_addr_str = get_config_file().get("validator")
        if not validator_addr_str:
            raise ClickException("no validator specified")

    return Web3.to_checksum_address(validator_addr_str)


def get_contract_address(contract_address_str: Optional[str]) -> str:
    """
    Get the contract address.  Fall back to 'CONTRACT_ADDRESS' env
    var, then config file 'contract_address' entry, then error.
    """
    if contract_address_str is None:
        contract_address_str = os.getenv(CONTRACT_ADDRESS_ENV_VAR)
        if contract_address_str is None:
            contract_address_str = get_config_file().get("contract_address")
            if contract_address_str is None:
                raise ClickException(
                    f"No contract address given (use --address, {CONTRACT_ADDRESS_ENV_VAR} "
                    f"env var or {CONFIG_FILE_NAME})"
                )

    return contract_address_str


def get_contract_abi(contract_abi_path: Optional[str]) -> str:
    """
    Get the contract abi file path.  Fall back to 'CONTRACT_ABI' env
    var, then config file 'contract_abi' entry, then error.
    """
    if contract_abi_path is None:
        contract_abi_path = os.getenv(CONTRACT_ABI_ENV_VAR)
        if contract_abi_path is None:
            contract_abi_path = get_config_file().get("contract_abi")
            if contract_abi_path is None:
                raise ClickException(
                    f"No contract ABI file given (use --abi, {CONTRACT_ABI_ENV_VAR} "
                    f"env var or {CONFIG_FILE_NAME})"
                )

    return contract_abi_path
