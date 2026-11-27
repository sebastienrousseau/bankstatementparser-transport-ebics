# bankstatementparser-transport-ebics

**EBICS** (Electronic Banking Internet Communication Standard) is the
protocol European corporates use to exchange payment and statement files
with their banks. **bankstatementparser-transport-ebics** covers the
parts of an EBICS exchange that are plain data:

| Concern | How this package handles it |
| :--- | :--- |
| Protocol versions | Builds EBICS 3.0 (`H005`) and 2.5 (`H004`) request envelopes |
| Order types | `STA`, `C53`, `C52`, `C54`, `Z53`, `INI`, `HIA`, `HPB`, `FDL`, `FUL` as `EbicsOrderType` |
| Keys | Holds `A006`, `X002` and `E002` key values; `INI`/`HIA` requests carry a SHA-256 digest of the signature key value |
| Responses | Reads the return code, report text, order and transaction IDs and base64 order data |
| Statements | Parses a statement payload you supply into `bankstatementparser` `Transaction` objects or a pandas DataFrame |

It opens **no network connection** and does **no signing, authentication
or encryption**: use it to build and inspect envelopes and to parse
statements you downloaded with another EBICS client. The
[Usage](usage.md) page has the details and the limits.

```python
from pathlib import Path

from bankstatementparser_transport_ebics import (
    EbicsClient,
    EbicsConfig,
    EbicsOrderType,
)

client = EbicsClient(
    EbicsConfig("EBICSBNK1", "PARTNER99", "USER01", "https://bank.example")
)
payload = Path("statement.xml").read_bytes()  # a CAMT.053 you downloaded
for tx in client.fetch_statement(EbicsOrderType.C53, mock_payload=payload):
    print(tx.booking_date, tx.amount, tx.currency, tx.description)
```

## In this manual

- [Usage](usage.md): requests, responses, statements and the limits.
- [Architecture](architecture.md): how the module is laid out.
- [The suite](suite.md): the `bankstatementparser` packages.
- [Comparison](COMPARISON.md) and [Benchmarks](BENCHMARKS.md).
- [Supported Python policy](POLICIES.md).
- [API reference](api.md), generated from the docstrings.
- [Changelog](changelog.md) and [Security policy](security.md).

The source, issues and releases live on
[GitHub](https://github.com/sebastienrousseau/bankstatementparser-transport-ebics);
the package is on
[PyPI](https://pypi.org/project/bankstatementparser-transport-ebics/).
