"""Shared test fixtures."""

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner() -> Iterator[CliRunner]:
    """CliRunner with isolated filesystem."""
    runner_ = CliRunner()
    with runner_.isolated_filesystem():
        yield runner_


@pytest.fixture
def autrc(runner: CliRunner) -> Callable[..., Path]:
    """Create a temporary .autrc file. Returns factory function."""

    def _make_autrc(**fields: str) -> Path:
        lines = ["[aut]\n"]
        for k, v in fields.items():
            lines.append(f"{k} = {v}\n")
        path = Path(".autrc")
        path.write_text("".join(lines))
        return path

    return _make_autrc
