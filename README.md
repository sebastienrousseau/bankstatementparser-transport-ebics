<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

<p align="center">
  <img src="https://cloudcdn.pro/bankstatementparser/v1/logos/bankstatementparser.svg" alt="bankstatementparser-transport-ebics logo" width="128" />
</p>

<h1 align="center">bankstatementparser-transport-ebics</h1>

<p align="center">
  Builds EBICS 3.0 and 2.5 request envelopes, reads EBICS responses and parses downloaded statements into bankstatementparser transactions.
</p>

<p align="center">
  <a href="https://github.com/sebastienrousseau/bankstatementparser-transport-ebics/actions"><img src="https://img.shields.io/github/actions/workflow/status/sebastienrousseau/bankstatementparser-transport-ebics/ci.yml?style=for-the-badge&logo=github" alt="Build" height="28" /></a>
  <a href="https://pypi.org/project/bankstatementparser-transport-ebics/"><img src="https://img.shields.io/pypi/v/bankstatementparser-transport-ebics?style=for-the-badge&color=fc8d62&logo=python" alt="Registry" height="28" /></a>
  <a href="https://sebastienrousseau.com/bankstatementparser-transport-ebics/"><img src="https://img.shields.io/badge/docs-user%20manual-0a7bbb?style=for-the-badge&labelColor=555555&logo=materialformkdocs" alt="Docs" height="28" /></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/sebastienrousseau/bankstatementparser-transport-ebics"><img src="https://img.shields.io/ossf-scorecard/github.com/sebastienrousseau/bankstatementparser-transport-ebics?style=for-the-badge&label=OpenSSF%20Scorecard&logo=openssf" alt="OpenSSF Scorecard" height="28" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0%20OR%20MIT-blue.svg?style=for-the-badge" alt="License: Apache-2.0 OR MIT" height="28" /></a>
  <a href="https://github.com/sebastienrousseau/bankstatementparser-transport-ebics/blob/main/docs/POLICIES.md"><img src="https://img.shields.io/badge/python-3.10%2B-93450a.svg?style=for-the-badge&logo=python" alt="Python 3.10+" height="28" /></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/sebastienrousseau/bankstatementparser-transport-ebics/main/.github/demo.gif" alt="A terminal printing bankstatementparser-transport-ebics 0.0.36, then the two examples building INI and C53 requests, reading a C53 download response and parsing its CAMT.053 statement into two transactions" width="100%" />
</p>

---

## Contents

**Getting started**

- [Install](#install): PyPI, source
- [Requirements](#requirements): toolchain floor, platforms
- [Quick Start](#quick-start): parse a statement you downloaded over EBICS

**The bankstatementparser-transport-ebics ecosystem**

- [The bankstatementparser-transport-ebics ecosystem](#the-bankstatementparser-transport-ebics-ecosystem): the core library, the loaders, writers and servers

**Library reference**

- [Capabilities at a glance](#capabilities-at-a-glance): the current surface by theme
- [Ecosystem comparison](#ecosystem-comparison): short matrix; full table at [`docs/COMPARISON.md`](docs/COMPARISON.md)
- [Benchmarks](#benchmarks): headline numbers; full table at [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md)
- [Features](#features): the public API
- [Configuration](#configuration): `EbicsConfig` and `EbicsKeyStore`
- [Examples](#examples): runnable example index

**Operational**

- [When not to use bankstatementparser-transport-ebics](#when-not-to-use-bankstatementparser-transport-ebics): limitations
- [Development](#development): make targets, fuzzing, CI
- [Security](#security): guarantees and compliance
- [Documentation](#documentation): all reference docs
- [Stability guarantees](#stability-guarantees): SemVer axis, output stability, minimum toolchain discipline
- [License](#license)

---

## Install

### As a Python library

```bash
pip install bankstatementparser-transport-ebics
```

That installs the package, `bankstatementparser >= 0.0.35` and pandas.

| Channel | Command | Notes |
| :--- | :--- | :--- |
| PyPI | `pip install bankstatementparser-transport-ebics` | Pulls in `bankstatementparser >= 0.0.35` |
| Source | `git clone https://github.com/sebastienrousseau/bankstatementparser-transport-ebics && cd bankstatementparser-transport-ebics && poetry install` | For local development |

Verify the installation:

```sh
python -c "import bankstatementparser_transport_ebics as e; print(e.__version__)"
# -> 0.0.36
```

An isolated virtual environment keeps its dependencies apart:

```sh
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
python -m pip install -U bankstatementparser-transport-ebics
```

---

## Requirements

- **Python 3.10 or later.** CI tests CPython 3.10, 3.11, 3.12, 3.13 and 3.14 on Linux, macOS and Windows; [`docs/POLICIES.md`](docs/POLICIES.md) says when the floor moves.
- **[`bankstatementparser`](https://pypi.org/project/bankstatementparser/) 0.0.35 or later**, which parses the statement payloads, and pandas, which it brings.
- **An EBICS client** to talk to your bank, if you need one: this package opens no connection (see [When not to use](#when-not-to-use-bankstatementparser-transport-ebics)).

---

## Quick Start

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

`fetch_statement` parses the payload with the core `bankstatementparser` and returns `Transaction` objects, debits negative. `fetch_and_parse` returns the same rows as a pandas DataFrame. The payload is named `mock_payload` because the package never downloads it itself.

---

## The bankstatementparser-transport-ebics ecosystem

`bankstatementparser` is a modular suite whose packages ship one version together. This package is its EBICS member; the full table, with every loader, writer and server, is in [The suite](docs/suite.md).

| Component | Purpose | Use case |
| :--- | :--- | :--- |
| [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) | The parser core: CAMT, pain.001, CSV, OFX, QFX, MT940 and PDF statements | Parsing statements from Python or the CLI |
| **`bankstatementparser-transport-ebics`** | EBICS envelopes, responses and statement payloads | Reading what an EBICS download returns |
| Loaders | BAI2, MT942, CFONB, CAMT.054, SEPA and BACS | Formats beyond the core |
| Writers | XLSX, QIF, OFX and SWIFT MT940/MT942 | Exporting parsed transactions |
| [`bankstatementparser-mcp`](https://github.com/sebastienrousseau/bankstatementparser-mcp) and [`bankstatementparser-lsp`](https://github.com/sebastienrousseau/bankstatementparser-lsp) | Model Context Protocol and Language Server Protocol servers | AI agents and editors |

---

## Capabilities at a glance

| Area | Capability | Status |
| :--- | :--- | :--- |
| Protocol versions | EBICS 3.0 (`H005`) and EBICS 2.5 (`H004`) request envelopes | Shipped |
| Order types | `STA` (MT940), `C53` (CAMT.053), `C52` (CAMT.052), `C54` (CAMT.054), `Z53`, `INI`, `HIA`, `HPB`, `FDL`, `FUL` | Shipped as `EbicsOrderType` |
| Requests | `INI`/`HIA` initialisation and download requests with an optional date range | Shipped |
| Keys | Holds `A006`, `X002` and `E002` key values; `INI`/`HIA` requests carry a SHA-256 digest of the signature key value | Shipped |
| Responses | Return code, report text, order and transaction IDs, base64 order data | Shipped |
| Statements | A payload you supply, parsed into `Transaction` objects or a DataFrame | Shipped |
| Network transport | Sending requests to the bank | Not implemented |
| Signing and encryption | `A006` signatures, `X002` authentication, `E002` encryption and decryption | Not implemented |

---

## Ecosystem comparison

The choice is between this package, which handles EBICS data, and a full EBICS client that talks to the bank. Every cell comes from this repository or the other project's PyPI description.

| Project | Talks to the bank | Signing and encryption | Licence |
| :--- | :---: | :---: | :---: |
| **bankstatementparser-transport-ebics** | No | No | Apache-2.0 OR MIT |
| [`fintech`](https://pypi.org/project/fintech/) (joonis) | Yes | Yes | Free to use but restricted |

See [`docs/COMPARISON.md`](docs/COMPARISON.md) for the evidence and complete matrix.

---

## Benchmarks

`benches/bench_ebics.py` times reading a C53 download response and parsing its CAMT.053 statement as the statement grows. Reading the envelope is linear at about 0.9 ms per MiB; parsing the statement costs a fixed 18 ms or so per call plus about 67 us per entry.

| Scenario | Result | Environment |
| :--- | ---: | :--- |
| `parse_response`, 5,000-entry statement (1.5 MiB) | 1.37 ms | Apple M1 Pro, macOS 27.2.1, CPython 3.12.16 |
| `fetch_statement`, 100 entries | 24.2 ms | Apple M1 Pro, macOS 27.2.1, CPython 3.12.16 |
| `fetch_statement`, 5,000 entries | 350 ms | Apple M1 Pro, macOS 27.2.1, CPython 3.12.16 |

See [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md) for methodology and full results.

---

## Features

The public API, all exported from `bankstatementparser_transport_ebics`:

- `EbicsConfig(host_id, partner_id, user_id, url, version="H005")`: credentials and endpoint configuration.
- `EbicsKeyStore(signature_key, authentication_key, encryption_key, bank_public_key)`: key values; `get_public_digest()` returns the SHA-256 digest of the signature key.
- `EbicsClient(config, key_store=None)`: `build_initialization_request`, `build_download_request`, `parse_response`, `fetch_statement`, `fetch_and_parse`.
- `EbicsResponse`: `return_code`, `report_text`, `order_id`, `transaction_id`, `payload`, `is_segment_complete` and the `is_success` property (`True` only for an explicit `000000`, `011000` or `011001`).
- `EbicsOrderType`: the order types listed above.
- `fetch_statement(config, order_type, start_date, end_date, mock_payload)`: convenience helper returning `list[Transaction]`.
- `fetch_and_parse(config, order_type, start_date, end_date, mock_payload)`: convenience helper returning a `pandas.DataFrame`.

The [Usage](docs/usage.md) page describes each request and response field.

---

## Configuration

There is no configuration file or environment variable. Everything is passed in code: `EbicsConfig` carries the host, partner and user IDs, the endpoint URL (stored, never contacted), the protocol version (`H005` or `H004`) and the security medium (default `0000`); `EbicsKeyStore` carries the key values. Without a key store the client uses placeholder key values, so pass your own before you rely on the digest in an `INI` request.

---

## Examples

[`examples/`](examples/) holds two runnable scripts, each run in CI against the fixtures in [`examples/data/`](examples/data/):

| Example | Demonstrates |
| :--- | :--- |
| [`01_basic_usage.py`](examples/01_basic_usage.py) | Building an `INI` and a `C53` request, then reading a C53 download response |
| [`02_advanced_workflow.py`](examples/02_advanced_workflow.py) | Parsing that response's CAMT.053 statement into transactions and a DataFrame |

---

## When not to use bankstatementparser-transport-ebics

- **You need to talk to your bank.** There is no network transport: `EbicsConfig.url` is stored but never contacted, and `fetch_statement` and `fetch_and_parse` parse only the payload passed as `mock_payload`, returning nothing when none is given.
- **You need signing or encryption.** Requests are not signed (`A006`), authenticated (`X002`) or encrypted (`E002`), and responses are not verified or decrypted. Real order data arrives compressed and encrypted; this package only base64-decodes it.
- **You need segmented downloads.** Multi-part transfers are not reassembled; only `is_segment_complete` is reported.
- **You pass untrusted IDs.** Request XML is built by string formatting without escaping.

Use it to build and inspect EBICS envelopes and to parse statements you have already downloaded with another EBICS client; do not use it as the connection to your bank.

---

## Development

```bash
git clone https://github.com/sebastienrousseau/bankstatementparser-transport-ebics.git
cd bankstatementparser-transport-ebics
poetry install
make check
```

`make check` runs the local gates: `ruff` lint and format, `mypy --strict`, Bandit, the complexity baseline (`scripts/check_complexity.py`), `pytest` with a 100% line and branch coverage floor, `interrogate` at 100% docstring coverage, the examples and the README template check. Other targets: `make bench`, `make fuzz` (Atheris, 60 s, Linux x86_64 with Python 3.12+), `make docs` (the MkDocs manual, `--strict`), `make audit` (`pip-audit` on the locked sets) and `make demo` (re-renders the GIF above with VHS from `.github/demo.tape`). CI adds the OS by Python matrix, the fuzz job, CodeQL and the Docs Lint gates. [`CONTRIBUTING.md`](CONTRIBUTING.md) covers the workflow and commit rules.

---

## Security

- **No network, no secrets in transit.** The package sends nothing; key values stay in the `EbicsKeyStore` you build.
- **Response parsing** is substring extraction, not an XML parser: no entity expansion and no external entities. `fuzz/fuzz_parse_response.py` fuzzes it with Atheris in CI and fails on any exception, on a verdict reported for a response with no return code, or on an inconsistent segment flag.
- **Statement payloads** go through a temporary file that is deleted after parsing, and the XML is read by the core `bankstatementparser`.
- **Supply chain.** Dependencies are locked in `poetry.lock`, CI installs hash-pinned exports of it, and `pip-audit`, Bandit and CodeQL run on every change. Releases publish to PyPI through OIDC trusted publishing and carry cosign signatures, SLSA provenance and SBOMs; every workflow action is pinned by commit SHA except the SLSA generator, which must be referenced by tag.

Report vulnerabilities according to [`SECURITY.md`](SECURITY.md).

---

## Documentation

- **User manual:** [sebastienrousseau.com/bankstatementparser-transport-ebics](https://sebastienrousseau.com/bankstatementparser-transport-ebics/), built from [`docs/`](docs/) with MkDocs
- **API reference:** [the manual's API page](https://sebastienrousseau.com/bankstatementparser-transport-ebics/api/), generated from the docstrings
- **Developer docs:** [`CONTRIBUTING.md`](CONTRIBUTING.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`GOVERNANCE.md`](GOVERNANCE.md), [`SUPPORT.md`](SUPPORT.md)
- **The suite:** [`docs/suite.md`](docs/suite.md), with every `bankstatementparser` package
- **History:** [`CHANGELOG.md`](CHANGELOG.md)

---

## Stability guarantees

- **Versioning.** Releases stay on the `0.0.x` line and step by exactly `0.0.1`, in lockstep with the rest of the `bankstatementparser` suite. Under SemVer a `0.0.x` release may break anything; this project names each break in the CHANGELOG instead.
- **The breaking axis is the output**: the XML a request builder emits, the fields `parse_response` reads and how it decides success, and the `Transaction` rows a statement produces. A change to any of those is called out in the CHANGELOG as breaking, even when no Python signature moves.
- **Python API.** The names exported from `bankstatementparser_transport_ebics` keep their names and fields; names starting with `_` are internal.
- **Minimum toolchain.** Python 3.10 is the floor; it moves only in a release, for the whole suite at once, with the reason in the CHANGELOG ([`docs/POLICIES.md`](docs/POLICIES.md)).

---

## License

Dual-licensed under [Apache License, Version 2.0](LICENSE-APACHE) or [MIT](LICENSE-MIT), at your option (`SPDX-License-Identifier: Apache-2.0 OR MIT`). Any contribution submitted for inclusion in the work shall be dual-licensed as above, without additional terms or conditions.
