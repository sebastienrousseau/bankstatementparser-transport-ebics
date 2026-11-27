# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Build EBICS requests and read a bank's response.

Builds an INI key-initialisation request and a C53 (CAMT.053) download
request for EBICS 3.0, then parses the download response in
``examples/data/c53_download_response.xml``: its return code, IDs and
order data. Nothing is sent anywhere; this package opens no connection.

The fixture carries the statement as plain base64. A real bank
compresses and encrypts order data (E002), which this package does not
undo; see the README's "When not to use" section.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from bankstatementparser_transport_ebics import (
    EbicsClient,
    EbicsConfig,
    EbicsOrderType,
)

DATA = Path(__file__).resolve().parent / "data"


def main() -> None:
    """Build two requests and parse one response."""
    config = EbicsConfig(
        host_id="EBICSBNK1",
        partner_id="PARTNER99",
        user_id="USER01",
        url="https://ebics.bank.example/ebics",
        version="H005",
    )
    client = EbicsClient(config)

    ini = client.build_initialization_request("INI")
    print(f"INI request: {len(ini)} characters, version {config.version}")

    download = client.build_download_request(
        EbicsOrderType.C53, date(2026, 1, 1), date(2026, 1, 31)
    )
    print(f"C53 request: {len(download)} characters, 2026-01-01..2026-01-31")

    raw = (DATA / "c53_download_response.xml").read_bytes()
    response = client.parse_response(raw)
    print(
        f"Response: return code {response.return_code} "
        f"(success={response.is_success}), order {response.order_id}, "
        f"transaction {response.transaction_id}"
    )
    print(f"Order data: {len(response.payload)} bytes of CAMT.053")


if __name__ == "__main__":
    main()
