# Security

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Research / best-effort |

## Reporting a vulnerability

Please open a GitHub security advisory (or private report to the maintainer) for issues in the **software** (e.g. path traversal in capture readers, unsafe deserialization).

Do **not** use the issue tracker to request help bypassing vehicle immobilizers, airbags, or other safety systems.

## Automotive safety note

OpenDashCAN defaults to **no CAN transmit**. Enabling TX on a real vehicle can create dangerous display or control conditions. See [docs/safety.md](docs/safety.md).
