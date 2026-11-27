# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Turn a downloaded CAMT.053 statement into transactions.

Takes the order data out of an EBICS download response
(``examples/data/c53_download_response.xml``) and parses it with
``fetch_statement`` into ``Transaction`` objects, then with
``fetch_and_parse`` into a pandas DataFrame. The statement is the one in
``examples/data/camt053_statement.xml``.
"""

from __future__ import annotations

from pathlib import Path

from bankstatementparser_transport_ebics import (
    EbicsClient,
    EbicsConfig,
    EbicsOrderType,
    fetch_and_parse,
)

DATA = Path(__file__).resolve().parent / "data"


def main() -> None:
    """Parse the response's statement into transactions and a frame."""
    config = EbicsConfig(
        "EBICSBNK1", "PARTNER99", "USER01", "https://ebics.bank.example"
    )
    client = EbicsClient(config)
    response = client.parse_response(
        (DATA / "c53_download_response.xml").read_bytes()
    )

    transactions = client.fetch_statement(
        order_type=EbicsOrderType.C53, mock_payload=response.payload
    )
    print(f"{len(transactions)} transactions:")
    for tx in transactions:
        print(
            f"  {tx.booking_date} {tx.amount:>8} {tx.currency} "
            f"{tx.description}"
        )

    frame = fetch_and_parse(
        config, EbicsOrderType.C53, mock_payload=response.payload
    )
    print(f"DataFrame columns: {', '.join(frame.columns)}")
    print(f"Net movement: {frame['amount'].sum():.2f} EUR")


if __name__ == "__main__":
    main()
