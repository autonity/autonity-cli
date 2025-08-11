# Autonity CLI

A command-line tool that exposes all the functionality of Autonity from the
convenience of the command-line. It can be used interactively or executed from a
shell script. Connecting directly to the Autonity JSON-RPC endpoint of your
choice, it allows you to:

- create new ATN and NTN accounts or import keys
- list balances for any native asset or ERC-20 token
- transfer assets to different account
- sign or verify messages using private/public keys
- make smart contract calls from the command-line
- query block information or protocol state
- manage the your validator node state
- delegate stake and claim staking rewards

After installing, run `aut --help` for a list of all commands and options.

## Quick Start

Requirements:

- **Python 3.9 or greater** (Install using the package manager for your OS or
  [pyenv](https://github.com/pyenv/pyenv) ).
  - (Note that websocket connections are not supported for Python 3.10+ due to
    an issue in the latest stable version of the `web3.py` dependency)
- **The** [pipx](https://pypa.github.io/pipx/) **tool** (Install a recent
  version with `pip install pipx`)

To install Autonity CLI as a pipx package, isolated in its own environment, run:

```console
pipx install autonity-cli
```

Once successfully installed, the tool will be available in the shell as the
`aut` command. All commands are discoverable from the help text. Type
`aut --help`, `aut <command> --help` etc. for details.

⚠️ To upgrade from using a _development build_ installed from Github, you will
need to switch back to the stable package by running:

```sh
pipx install --force autonity-cli
```

⚠️ If upgrading from "aut" `v0.5.0` or earlier, you will need to uninstall the
`aut` package before reinstalling `autonity-cli`:

```console
$ pipx uninstall aut
$ pipx install autonity-cli
```

**Note:**

- If `pipx` selects an incompatible version of Python, you may need to specify a
  specific one. Use the `--python` flag:

  ```console
  pipx install --python /usr/bin/pythonX.Y autonity-cli
  ```

  See the `pipx install` help text for details.

- If the `aut` command is not available after installation, and you are on
  Ubuntu, try running `aut` in a new terminal window. Otherwise, ensure that
  `~/.local/bin` appears in your `PATH`. Run `pipx ensurepath` to verify.

## Authentication

Autonity CLI supports the following authentication methods for signing messages
and transactions:

- Trezor device
- local keyfile

### Trezor authentication

Before using a Trezor device with Autonity CLI, ensure it is running the latest
firmware version, or a firmware version that is supported by
[trezorlib](https://github.com/trezor/trezor-firmware/blob/main/python/README.md#firmware-version-requirements).

To authenticate with a connected Trezor device, pass the `--trezor ACCOUNT`
option to the relevant command, where `ACCOUNT` is either:

- the _full derivation path_ of the account, for example: `m/44h/60h/0h/0/123`
- the _index of the account_ at the default Trezor derivation prefix for
  Ethereum coins `m/44h/60h/0h/0`, for example: `123`

The following two options are equivalent:

- `--trezor 123`
- `--trezor m/44h/60h/0h/0/123`

### Local keyfile authentication

To authenticate with a local keyfile, pass the `--keyfile PATH` option, where
`PATH` is the relative or absolute path of the encrypted keyfile to use.

Once the keyfile is loaded, Autonity CLI will normally issue a prompt for the
password to decrypt the key. But if the environment variable `KEYFILEPWD` has
been set, then Autonity CLI will skip the password prompt and attempt to use the
value of this variable as the keyfile password instead.

## (Optional) Enable command completion (bash and zsh)

Completion is available in `bash` and `zsh` shells as follows. (Adapt these
commands to your particular configuration.)

```console
# For zsh, replace bash_source with zsh_source.
$ _AUT_COMPLETE=bash_source aut > ~/.aut-complete
$ echo 'source ~/.aut-complete' >> ~/.bashrc
```

Auto-complete should be enabled in _new_ shells. (Use `source ~/.aut-complete`
to activate it in the current shell instance.)

## Configuration using `.autrc` files

If the `aut` command finds this file, it reads configuration parameters from it.
See the [sample file](.autrc.sample) in this repo. This avoids the need to enter
certain values on the command-line. These parameters can be overridden by
environment variables and command-line parameters where necessary.

If `.autrc` is not found in the current directory, all parent directories are
searched in turn and the first `.autrc` file found is used. Alternatively, this
file can be placed in `~/.config/aut/autrc`.

A very simple `.autrc` file may specify the endpoint for Web3 connections:

```console
# Create a config file holding the rpc endpoint.
$ echo '[aut]' > .autrc
$ echo 'rpc_endpoint = https://rpc1.piccadilly.autonity.org/' >> .autrc
```

## Usage Examples

### Create a new account (for demo purposes)

```console
# Create an account
# !! For demonstration purposes only. Use a HW wallet or other key-management infrastructure. !!
$ mkdir -p keystore
$ aut account new --keyfile keystore/alice.key
Password for new account:
Confirm account password:
0xd888bc90720757796C72eC2a3A231c81b55e8097
```

This can be added as the default key for transaction signing (and default
address for queries) in the `.autrc` file:

```console
echo 'keyfile = keystore/alice.key' >> .autrc
```

### Check account balance (after funding the account)

```console
# Check Alice's balance (use address in keystore/alice.key), given in Wei.
$ aut account balance
100000000000000000000
# Check Bob's balance (1 ATN).  Bob's address is 0x4EcE2e62E67a7B64a83D3E180dC86962145b762f
$ aut account balance 0x4EcE2e62E67a7B64a83D3E180dC86962145b762f
1000000000000000000
```

### Create, sign and send a transaction

```console
# Send 1 ATN to Bob
$ aut tx make --to 0x4EcE2e62E67a7B64a83D3E180dC86962145b762f --value 1aut | aut tx sign - | aut tx send -
Enter passphrase (or CTRL-d to exit):
0x47f71a94372d00a3066414b80f3b9c78d71b3011479ddc86e37ab86e0fe80d8a
```

Explanation of the above: The `maketx` command extracts the `from` address from
the default keyfile, and automatically sets the `gas`, `nonce` and other fields
by querying the RPC endpoint in the config file. It then writes this to
`stdout`, which is piped to the `signtx` command, using the `-` argument to
indicate `stdin`. The sign `signtx` decrypts the default keyfile after querying
the user for the password, and writes the signed transaction to `stdout`. This
is then piped to the `sendtx` command, which connects to the RPC endpoint given
in the config file and passes the signed transaction to the node for broadcast.
`sendtx` then outputs the transaction hash to `stdout`.

All configuration options can be set using command-line parameters to override
the configuration file. Use the `--help` flag with any command to see all
available options.

### Wait for the transaction

```console
# Wait for a transaction to complete.  Print the transaction receipt to stdout.
$ aut tx wait 0x47f71a94372d00a3066414b80f3b9c78d71b3011479ddc86e37ab86e0fe80d8a
{"blockHash": "0x65e74faaaee5efa3b6e998fd78c8e1ca3085c8bd88709101e8fa801a03ab371d", "blockNumber": 5780419, "contractAddress": null, "cumulativeGasUsed": 21000, "effectiveGasPrice": 1000000000, "from": "0xd888bc90720757796C72eC2a3A231c81b55e8097", "gasUsed": 21000, "logs": [], "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", "status": 1, "to": "0x4EcE2e62E67a7B64a83D3E180dC86962145b762f", "transactionHash": "0x47f71a94372d00a3066414b80f3b9c78d71b3011479ddc86e37ab86e0fe80d8a", "transactionIndex": 0, "type": "0x2"}

# Re-check Bob's balance
$ aut account balance 0x4EcE2e62E67a7B64a83D3E180dC86962145b762f
2000000000000000000
```

### Call contracts

Contract calls are possible using the following syntax:

```console
aut contract call --address CONTRACT_ADDRESS --abi ABI_FILE METHOD [PARAMETERS]...
```

As an example, assuming that the RPC URL has been set in the `.autrc` file,
calling the `getProposer` function of the Autonity contract is

```console
$ aut contract call --abi <((aut protocol contract-abi)) --address $(aut protocol contract-address) \
  getProposer 10000 1
"0x31870f96212787D181B3B2771F58AF2BeD0019Aa"
```

#### Complex types

The types `array` and `tuple` are supported as parameters as single quoted
strings.

For example, giving a contract function `arrayLength` that takes a `string[]`
input, the command will look like the following:

```console
$ aut contract call --abi ABI_FILE_PATH --address CONTRACT_ADDRESS \
  arrayLength '["a","b","c","d","e","f","g"]'
7
```

The same applies to `tuple` types, giving a struct:

```solidity
struct Payment {
    address from;
    uint256 blockNumber;
    uint256 amount;
}
```

A contract call `printHeight` that accepts a `Payment` as input will be:

```console
$ aut contract call --abi ABI_FILE_PATH --address CONTRACT_ADDRESS  \
  printHeight '["0x31870f96212787D181B3B2771F58AF2BeD0019Aa", 183413, 1000000000000000000]'
183413
```

## Development

The project is managed using [hatch](https://hatch.pypa.io/latest/). Check the
installation instructions [here](https://hatch.pypa.io/latest/install/).

Hatch will automatically manage a virtual environment for the project. To run
the command in development mode use:

```console
hatch run aut ....
```

alternatively, you can open a shell in the `hatch` environment by executing

```console
hatch shell
```

To run the unit and script-based tests, use `hatch run test`. To check for
linting errors, use `hatch run lint:all`. To reformat the code, use
`hatch run lint:format`.

## Reporting a Vulnerability

**Please do not file a public ticket** mentioning the vulnerability.

Instead, please send an email to <security@autonity.org> to report a security
issue.

The following PGP key may be used to communicate sensitive information to
developers:

Fingerprint: `6006 CCC3 DD11 7885 1A23 4290 7486 F832 6320 219E`

```
-----BEGIN PGP PUBLIC KEY BLOCK-----

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
VtiVUMzKBEpmz4LdeSy73Qfr
=12PL
-----END PGP PUBLIC KEY BLOCK-----
```
