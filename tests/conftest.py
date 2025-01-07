import json

from click.testing import CliRunner
from eth_account.signers.local import LocalAccount
from eth_keyfile import keyfile
import pytest


@pytest.fixture
def runner(w3):
    runner_ = CliRunner()
    with runner_.isolated_filesystem():
        with open(".autrc", "w") as f:
            f.writelines([
                "[aut]\n",
                f"rpc_endpoint = {w3.provider.endpoint_uri}\n"
            ])
        yield runner_


@pytest.fixture
def operator_keyfile(runner, operator):
    filename = "operator.key"
    _create_keyfile_json(operator, filename)
    yield filename


@pytest.fixture
def user_keyfile(runner, user):
    filename = "user.key"
    _create_keyfile_json(user, filename)
    yield filename


def _create_keyfile_json(account: LocalAccount, filename: str) -> None:
    with open(filename, "w") as f:
        json.dump(keyfile.create_keyfile_json(account.key, b""), f)
