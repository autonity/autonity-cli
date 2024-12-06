# Changelog

## TBD

### Changed

- Support the Autonity Tiber protocol ([#176](https://github.com/autonity/autonity-cli/pull/176))
- Support Python 3.13 & drop Python 3.8 support ([`e8766e3`](https://github.com/autonity/autonity-cli/commit/e8766e3))

## [v0.6.0] - 2024-10-23

### Changed

- Rename the package to `autonity-cli` ([#172](https://github.com/autonity/autonity-cli/pull/172))

## [v0.5.0] - 2024-07-03

### Changed

- Support the Autonity Yamuna protocol ([#158](https://github.com/autonity/autonity-cli/pull/158))
- Drop `get-` prefix from protocol commands ([#159](https://github.com/autonity/autonity-cli/issues/159))
- Move governance commands into `aut governance` ([`b656ec4`](https://github.com/autonity/autonity-cli/commit/b656ec4))

## [v0.4.0] - 2024-03-06

### Changed

- Support the Autonity Sumida protocol ([#146](https://github.com/autonity/autonity-cli/issues/146))
- Require consensus key for validator registration ([`380b6be`](https://github.com/autonity/autonity-cli/commit/380b6be))

### Added

- Support Python 3.12 ([#138](https://github.com/autonity/autonity-cli/issues/138))

### Fixed

- Fix `AssertionError` when `contract call` returns multiple values ([#127](https://github.com/autonity/autonity-cli/issues/127))
- Fix `TypeError` when `contract call` returns bytes values ([#141](https://github.com/autonity/autonity-cli/issues/141))

## [v0.3.0] - 2024-01-15

### Changed

- Require `oracle` address for validator registration ([`b7cf048`](https://github.com/autonity/autonity-cli/commit/b7cf048))

### Added

- Add commands for new Autonity Contract protocol functions ([`d63a425`](https://github.com/autonity/autonity-cli/commit/d63a425))
- Support the `-h` help flag in addition to `--help` ([`84ab6a1`](https://github.com/autonity/autonity-cli/commit/84ab6a1))

### Fixed

- Fix compatibility with Autonity Barada ([`f424804`](https://github.com/autonity/autonity-cli/commit/f424804))
- Fix potential crash when listing accounts ([`1886121`](https://github.com/autonity/autonity-cli/commit/1886121))
- Fix startup crash due to `ModuleNotFoundError` from eth_rlp ([#137](https://github.com/autonity/autonity-cli/issues/137))

[v0.6.0]: https://github.com/autonity/autonity-cli/releases/tag/v0.6.0
[v0.5.0]: https://github.com/autonity/autonity-cli/releases/tag/v0.5.0
[v0.4.0]: https://github.com/autonity/autonity-cli/releases/tag/v0.4.0
[v0.3.0]: https://github.com/autonity/autonity-cli/releases/tag/v0.3.0
