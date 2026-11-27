<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

<p align="center">
  <img
    src="https://cloudcdn.pro/bankstatementparser/v1/logos/bankstatementparser.svg"
    alt="bankstatementparser-transport-ebics logo"
    width="120"
    height="120"
  />
</p>

<h1 align="center">bankstatementparser-transport-ebics</h1>

<p align="center">
  <b>EBICS 3.0 & 2.5 transport protocol adapter and automated statement fetcher for bankstatementparser.</b>
</p>

<p align="center">
  <a href="https://github.com/sebastienrousseau/bankstatementparser-transport-ebics/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/sebastienrousseau/bankstatementparser-transport-ebics/ci.yml?branch=main&label=Tests&style=for-the-badge&logo=github" alt="Tests" height="28" /></a>
  <a href="https://pypi.org/project/bankstatementparser-transport-ebics/"><img src="https://img.shields.io/pypi/v/bankstatementparser-transport-ebics?style=for-the-badge&color=fc8d62&logo=python" alt="PyPI version" height="28" /></a>
  <a href="https://pypi.org/project/bankstatementparser-transport-ebics/"><img src="https://img.shields.io/pypi/pyversions/bankstatementparser-transport-ebics.svg?style=for-the-badge" alt="Python versions" height="28" /></a>
  <a href="https://pypi.org/project/bankstatementparser-transport-ebics/"><img src="https://img.shields.io/pypi/dm/bankstatementparser-transport-ebics.svg?style=for-the-badge" alt="PyPI downloads" height="28" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0%20OR%20MIT-blue.svg?style=for-the-badge" alt="License: Apache-2.0 OR MIT" height="28" /></a>
</p>

---

## Contents

- [What is bankstatementparser-transport-ebics?](#what-is-bankstatementparser-transport-ebics) — the problem it solves
- [Install](#install) — PyPI, virtualenv
- [Current limitations](#current-limitations) — what this release does not do yet
- [Quick start](#quick-start) — parse a downloaded statement payload
- [Public API](#public-api) — `EbicsClient`, `EbicsConfig`, `fetch_statement`, `fetch_and_parse`
- [Development](#development) — quality gates, tests
- [Ecosystem](#ecosystem) — modular package suite
- [Contributing](#contributing)
- [License](#license)

---

## What is bankstatementparser-transport-ebics?

**EBICS** (Electronic Banking Internet Communication Standard) is the secure, multi-bank communication protocol mandatory across European and global corporate treasury operations.

**bankstatementparser-transport-ebics** builds EBICS 3.0 (`H005`) and 2.5 (`H004`) request envelopes, reads the return code and order data out of EBICS responses, and parses statement payloads (`STA`, `C53`, `C54`) into `bankstatementparser` transactions. It does not yet talk to a bank server itself: see [Current limitations](#current-limitations).

| Concern | How this adapter handles it |
| :--- | :--- |
| **Protocol Versions** | Supports EBICS 3.0 (`H005`) and EBICS 2.5 (`H004`) XML envelopes |
| **Order Types** | `STA` (MT940), `C53` (CAMT.053), `C52` (CAMT.052), `C54` (CAMT.054), `INI`, `HIA`, `HPB` |
| **Keys** | Holds `A006`, `X002` and `E002` key values; `INI`/`HIA` requests carry a SHA-256 digest of the signature key |
| **Direct Ingestion** | Parses a statement payload you supply into unified `Transaction` objects |

---

## Current limitations

- **No network transport.** `EbicsConfig.url` is stored but never
  contacted. `fetch_statement` and `fetch_and_parse` parse the payload
  passed as `mock_payload` and return nothing when none is given.
- **No signing or encryption.** Requests are not signed (`A006`),
  authenticated (`X002`) or encrypted (`E002`), and responses are not
  verified or decrypted.

Use it to build and inspect EBICS envelopes and to parse statements you
have already downloaded with another EBICS client; do not use it as the
connection to your bank.

---

## Install

| Channel | Command | Notes |
| :--- | :--- | :--- |
| PyPI | `pip install bankstatementparser-transport-ebics` | Pulls in `bankstatementparser >= 0.0.35` |
| Source | `git clone https://github.com/sebastienrousseau/bankstatementparser-transport-ebics && cd bankstatementparser-transport-ebics && poetry install` | For local development |

Requires Python 3.10 or later. Compatible with macOS, Linux, and Windows.

<details>
<summary>Using an isolated virtual environment (recommended)</summary>

```sh
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
python -m pip install -U bankstatementparser-transport-ebics
```

</details>

---


## Quick start

```python
from pathlib import Path

from bankstatementparser_transport_ebics import EbicsClient, EbicsConfig, EbicsOrderType

config = EbicsConfig(
    host_id="EBICSBNK1",
    partner_id="PARTNER99",
    user_id="USER01",
    url="https://ebics.bank.com/ebics",
    version="H005",  # EBICS 3.0
)

client = EbicsClient(config)

# Parse a CAMT.053 statement downloaded with another EBICS client
payload = Path("statement.xml").read_bytes()
transactions = client.fetch_statement(
    order_type=EbicsOrderType.C53, mock_payload=payload
)
for tx in transactions:
    print(f"{tx.booking_date} | {tx.description} | {tx.amount} {tx.currency}")
```

---

## Public API

- `EbicsConfig(host_id, partner_id, user_id, url, version="H005")`: Credentials and endpoint configuration.
- `EbicsClient(config, key_store=None)`: Main transport client with `build_initialization_request`, `build_download_request`, `parse_response`, `fetch_statement`, `fetch_and_parse`.
- `fetch_statement(config, order_type, start_date, end_date, mock_payload)`: Convenience helper returning `list[Transaction]`.
- `fetch_and_parse(config, order_type, start_date, end_date, mock_payload)`: Convenience helper returning `pandas.DataFrame`.

---

## Development

The project enforces strict code-quality gates: 100% test and branch coverage, strict type annotations (`mypy`), style linting (`ruff`), docstring coverage (`interrogate`), and security scanning (`bandit`).

```bash
# Run test suite with branch coverage enforcement
poetry run pytest

# Type checking and linting
poetry run mypy .
poetry run ruff check .
poetry run ruff format --check .

# Documentation and security gates
poetry run interrogate -v
poetry run bandit -r . -c pyproject.toml
```

---


## Ecosystem

`bankstatementparser` is part of a modular financial ecosystem. Optional companion packages provide specialized loaders, writers, AI agents, language servers, and transport protocol adapters:

| Package | GitHub Repository | PyPI | Role | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`bankstatementparser`** | [`sebastienrousseau/bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser.svg)](https://pypi.org/project/bankstatementparser/) | Core Engine | Unified parser for CAMT (052/053), PAIN.001, CSV, OFX, QFX, MT940, and PDF statements |
| **`bankstatementparser-mcp`** | [`sebastienrousseau/bankstatementparser-mcp`](https://github.com/sebastienrousseau/bankstatementparser-mcp) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-mcp.svg)](https://pypi.org/project/bankstatementparser-mcp/) | AI Protocol | Model Context Protocol (MCP) server exposing statement tools to LLMs & AI agents |
| **`bankstatementparser-lsp`** | [`sebastienrousseau/bankstatementparser-lsp`](https://github.com/sebastienrousseau/bankstatementparser-lsp) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-lsp.svg)](https://pypi.org/project/bankstatementparser-lsp/) | Developer Tooling | Language Server Protocol (LSP) with live SWIFT MT940 statement validation & diagnostics |
| **`bankstatementparser-transport-ebics`** | [`sebastienrousseau/bankstatementparser-transport-ebics`](https://github.com/sebastienrousseau/bankstatementparser-transport-ebics) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-transport-ebics.svg)](https://pypi.org/project/bankstatementparser-transport-ebics/) | Transport | Automated bank statement retrieval over EBICS 3.0 (`H005`) and 2.5 (`H004`) protocols |
| **`bankstatementparser-writer-xlsx`** | [`sebastienrousseau/bankstatementparser-writer-xlsx`](https://github.com/sebastienrousseau/bankstatementparser-writer-xlsx) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-writer-xlsx.svg)](https://pypi.org/project/bankstatementparser-writer-xlsx/) | Output Writer | Formats and exports parsed banking transactions into styled Microsoft Excel (`.xlsx`) workbooks |
| **`bankstatementparser-writer-qif`** | [`sebastienrousseau/bankstatementparser-writer-qif`](https://github.com/sebastienrousseau/bankstatementparser-writer-qif) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-writer-qif.svg)](https://pypi.org/project/bankstatementparser-writer-qif/) | Output Writer | Serializes transactions into standard Quicken Interchange Format (`.qif`) exchange files |
| **`bankstatementparser-writer-ofx`** | [`sebastienrousseau/bankstatementparser-writer-ofx`](https://github.com/sebastienrousseau/bankstatementparser-writer-ofx) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-writer-ofx.svg)](https://pypi.org/project/bankstatementparser-writer-ofx/) | Output Writer | Serializes transactions into standard Open Financial Exchange (`.ofx`) XML/SGML files |
| **`bankstatementparser-writer-swift`** | [`sebastienrousseau/bankstatementparser-writer-swift`](https://github.com/sebastienrousseau/bankstatementparser-writer-swift) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-writer-swift.svg)](https://pypi.org/project/bankstatementparser-writer-swift/) | Output Writer | Exports transactions to SWIFT MT940 customer statements and MT942 interim reports |
| **`bankstatementparser-loader-bai2`** | [`sebastienrousseau/bankstatementparser-loader-bai2`](https://github.com/sebastienrousseau/bankstatementparser-loader-bai2) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-bai2.svg)](https://pypi.org/project/bankstatementparser-loader-bai2/) | Input Loader | Parses BAI2 cash-management and account balance statements |
| **`bankstatementparser-loader-mt942`** | [`sebastienrousseau/bankstatementparser-loader-mt942`](https://github.com/sebastienrousseau/bankstatementparser-loader-mt942) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-mt942.svg)](https://pypi.org/project/bankstatementparser-loader-mt942/) | Input Loader | Parses SWIFT MT942 interim transaction reports with credit/debit summary reconciliation |
| **`bankstatementparser-loader-cfonb`** | [`sebastienrousseau/bankstatementparser-loader-cfonb`](https://github.com/sebastienrousseau/bankstatementparser-loader-cfonb) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-cfonb.svg)](https://pypi.org/project/bankstatementparser-loader-cfonb/) | Input Loader | Parses French CFONB 120 / AFB120 120-byte fixed-width banking statement files |
| **`bankstatementparser-loader-camt054`** | [`sebastienrousseau/bankstatementparser-loader-camt054`](https://github.com/sebastienrousseau/bankstatementparser-loader-camt054) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-camt054.svg)](https://pypi.org/project/bankstatementparser-loader-camt054/) | Input Loader | Ingests ISO 20022 CAMT.054 real-time debit/credit notification stream XML |
| **`bankstatementparser-loader-sepa`** | [`sebastienrousseau/bankstatementparser-loader-sepa`](https://github.com/sebastienrousseau/bankstatementparser-loader-sepa) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-sepa.svg)](https://pypi.org/project/bankstatementparser-loader-sepa/) | Input Loader | Ingests ISO 20022 SEPA PAIN.002 payment status reports and PAIN.008 direct debit mandates |
| **`bankstatementparser-loader-bacs`** | [`sebastienrousseau/bankstatementparser-loader-bacs`](https://github.com/sebastienrousseau/bankstatementparser-loader-bacs) | [![PyPI](https://img.shields.io/pypi/v/bankstatementparser-loader-bacs.svg)](https://pypi.org/project/bankstatementparser-loader-bacs/) | Input Loader | Parses UK BACS Standard 18 / Faster Payments 106-byte fixed-width transmission files |

---

## Contributing

Contributions are welcome! Please submit an issue or pull request on GitHub. Ensure that all quality gates pass and test coverage remains at 100%.

---

## License

This project is dual-licensed under the **Apache License 2.0** and the **MIT License**. See [LICENSE-APACHE](LICENSE-APACHE) and [LICENSE-MIT](LICENSE-MIT) for full details.

