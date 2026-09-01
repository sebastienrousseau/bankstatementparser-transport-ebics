# EBICS 3.0 & 2.5 Transport Adapter for Bank Statement Parser

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0_OR_MIT-blue.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/sebastienrousseau/bankstatementparser-transport-ebics)

EBICS (Electronic Banking Internet Communication Standard) 3.0 (`H005`) and 2.5 (`H004`) transport protocol adapter for automated statement fetching in [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser).

---

## Features

- **EBICS 3.0 & 2.5 Protocols**: Supports protocol versions `H005` (EBICS 3.0 / BTF) and `H004` (EBICS 2.5).
- **Automated Statement Ingest**: Requests and receives `C53` (CAMT.053), `C52` (CAMT.052), `C54` (CAMT.054), `STA` (MT940), and `Z53` compressed statements.
- **Key Initialization**: Generates initialization payloads for `INI`, `HIA`, and `HPB` handshakes.
- **Direct Parser Integration**: Transparently decodes payloads directly into unified `Transaction` objects and pandas DataFrames.

---

## Installation

```bash
pip install bankstatementparser-transport-ebics
```

---

## Quickstart

```python
from bankstatementparser_transport_ebics import EbicsConfig, fetch_statement

# 1. Define EBICS partner configuration
config = EbicsConfig(
    host_id="EBICSBNK1",
    partner_id="PARTNER99",
    user_id="USER01",
    url="https://ebics.bank.com/ebics",
)

# 2. Fetch and parse statement transactions directly
transactions = fetch_statement(config, order_type="C53")
for tx in transactions:
    print(f"{tx.booking_date} | {tx.description} | {tx.amount} {tx.currency}")
```

---

## License

Dual-licensed under Apache 2.0 and MIT.
