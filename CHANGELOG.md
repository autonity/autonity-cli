# Changelog

<!--
----------------------------
      Common Changelog
----------------------------
https://common-changelog.org
----------------------------

Template:

## [vX.Y.Z] - YYYY-MM-DD

### Changed

### Added

### Removed

### Fixed
-->

## [v2.0.1] - 2025-08-12

### Fixed

-  Fix user-supplied nonce being ignored ([`026ca94`](https://github.com/autonity/autonity-cli/commit/026ca94))

## [v2.0.0] - 2025-08-09

### Changed

- Support the Autonity Nile protocol ([#210](https://github.com/autonity/autonity-cli/pull/210))
- Prefix `reveal-private-key` output with `0x` ([#182](https://github.com/autonity/autonity-cli/pull/182))
- Include Autonity protocol version in `--version` ([#185](https://github.com/autonity/autonity-cli/pull/185))
- Group related command options in help text ([`606693b`](https://github.com/autonity/autonity-cli/commit/606693b))
- Shorten keyfile path in password prompt ([`fc3c96e`](https://github.com/autonity/autonity-cli/commit/fc3c96e))

### Added

- Support authenticating with a Trezor device ([#203](https://github.com/autonity/autonity-cli/pull/203))
- Implement `validator` commands `locked-balance-of` & `unlocked-balance-of` ([#189](https://github.com/autonity/autonity-cli/issues/161))

### Removed

- Remove insecure `--password` and `--show-password` options ([`b6bbb03`](https://github.com/autonity/autonity-cli/commit/b6bbb03), [`da1eb21`](https://github.com/autonity/autonity-cli/commit/da1eb21))
- Remove `account lntn-balances` command ([`8450dee`](https://github.com/autonity/autonity-cli/commit/8450dee))
- Remove `governance set-upgrade-manager-contract` command ([#188](https://github.com/autonity/autonity-cli/issues/188))

### Fixed

- Fix several help message typos and formatting ([#181](https://github.com/autonity/autonity-cli/pull/181))
- Fix `--pool-address` option of `set-withheld-rewards-pool` ([#191](https://github.com/autonity/autonity-cli/pull/191))

## [v1.0.0] - 2024-12-12

### Changed

- Support the Autonity Tiber protocol ([#176](https://github.com/autonity/autonity-cli/pull/176))

### Added

- Add `account` command `reveal-private-key` ([`c5c65e4`](https://github.com/autonity/autonity-cli/commit/c5c65e4))
- Add `protocol` command `contract-abi` ([`631cd36`](https://github.com/autonity/autonity-cli/commit/631cd36))
- Support Python 3.13 ([`4ae7370`](https://github.com/autonity/autonity-cli/commit/4ae7370))

### Removed

- Drop support for Python 3.8 ([`4ae7370`](https://github.com/autonity/autonity-cli/commit/4ae7370))

### Fixed

- Resolve clashing `-f` option in `verify-signature` ([#170](https://github.com/autonity/autonity-cli/issues/170))

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

<!-- [vX.Y.Z]: https://github.com/autonity/autonity.py/releases/tag/vX.Y.Z -->
[v2.0.1]: https://github.com/autonity/autonity-cli/releases/tag/v2.0.1
[v2.0.0]: https://github.com/autonity/autonity-cli/releases/tag/v2.0.0
[v1.0.0]: https://github.com/autonity/autonity-cli/releases/tag/v1.0.0
[v0.6.0]: https://github.com/autonity/autonity-cli/releases/tag/v0.6.0
[v0.5.0]: https://github.com/autonity/autonity-cli/releases/tag/v0.5.0
[v0.4.0]: https://github.com/autonity/autonity-cli/releases/tag/v0.4.0
[v0.3.0]: https://github.com/autonity/autonity-cli/releases/tag/v0.3.0
