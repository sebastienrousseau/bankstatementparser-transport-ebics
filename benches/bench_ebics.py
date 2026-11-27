#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""What it costs to read an EBICS download, as the statement grows.

A C53 download is one response whose order data is a whole day's
CAMT.053 statement, and its size follows how busy the account was, not
anything the caller chose. Two steps run on it, so both are measured:

* ``parse_response``: pull the return code, IDs and base64 order data
  out of the response envelope.
* ``fetch_statement``: parse that CAMT.053 statement into
  ``Transaction`` objects (through the core ``bankstatementparser``).

Read ``us/entry``. Flat means linear, and a month-end statement is fine.
Climbing means something rescans what it has already read.

Run::

    python benches/bench_ebics.py
    python benches/bench_ebics.py --json
    python benches/bench_ebics.py --quick     # what CI runs

Nothing here asserts a threshold: wall-clock is not comparable between
machines, and a flaky performance gate teaches people to ignore red. CI
runs ``--quick`` so a benchmark that has stopped running against the
current API fails the build instead of rotting into a file that reads as
verified and is not.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bankstatementparser_transport_ebics import (  # noqa: E402
    EbicsClient,
    EbicsConfig,
    EbicsOrderType,
)

HEAD = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
<BkToCstmrStmt><GrpHdr><MsgId>BENCH</MsgId></GrpHdr><Stmt><Id>S1</Id>
<Acct><Id><IBAN>FR7630006000011234567890189</IBAN></Id><Ccy>EUR</Ccy></Acct>
"""
ENTRY = """<Ntry><Amt Ccy="EUR">{amount}.00</Amt><CdtDbtInd>{side}</CdtDbtInd>
<BookgDt><Dt>2026-01-{day:02d}</Dt></BookgDt><NtryDtls><TxDtls>
<Refs><EndToEndId>E2E-{i}</EndToEndId></Refs>
<RmtInf><Ustrd>Payment {i}</Ustrd></RmtInf></TxDtls></NtryDtls></Ntry>
"""
TAIL = "</Stmt></BkToCstmrStmt></Document>\n"
RESPONSE = """<ebicsResponse xmlns="urn:org:ebics:H005" Version="H005">
<header><static><TransactionID>T1</TransactionID></static><mutable>
<OrderID>A001</OrderID><ReturnCode>000000</ReturnCode>
<ReportText>[EBICS_OK] OK</ReportText></mutable></header>
<body><DataTransfer><OrderData>{data}</OrderData></DataTransfer></body>
</ebicsResponse>"""


def statement(entries: int) -> str:
    """A CAMT.053 statement with ``entries`` alternating entries."""
    body = "".join(
        ENTRY.format(
            amount=(i % 900) + 100,
            side="CRDT" if i % 2 else "DBIT",
            day=(i % 28) + 1,
            i=i,
        )
        for i in range(entries)
    )
    return HEAD + body + TAIL


def _best(call: Callable[[], object], repeats: int) -> float:
    """Best-of timing after one untimed warm-up.

    The minimum is the least noisy estimator available; the mean follows
    whatever else the machine happens to be doing.
    """
    call()
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        call()
        samples.append(time.perf_counter() - start)
    return min(samples)


def measure(client: EbicsClient, entries: int, repeats: int) -> dict:
    """Time both steps on one statement size."""
    xml = statement(entries).encode("utf-8")
    response = RESPONSE.format(data=base64.b64encode(xml).decode("ascii"))
    envelope = _best(lambda: client.parse_response(response), repeats)
    payload = client.parse_response(response).payload

    def fetch() -> object:
        return client.fetch_statement(EbicsOrderType.C53, mock_payload=payload)

    parse = _best(fetch, repeats)
    found = len(client.fetch_statement(mock_payload=payload))
    return {
        "entries": entries,
        "transactions": found,
        "kib": len(response) / 1024,
        "envelope_ms": envelope * 1e3,
        "statement_ms": parse * 1e3,
        "us_per_entry": parse * 1e6 / entries,
    }


def run(quick: bool) -> list[dict]:
    """Measure every size; ``quick`` keeps it to what CI can afford."""
    client = EbicsClient(
        EbicsConfig("HOST", "PARTNER", "USER", "https://bank.invalid")
    )
    sizes, repeats = ([10, 100], 3) if quick else ([10, 100, 1_000, 5_000], 5)
    return [measure(client, n, repeats) for n in sizes]


def render(rows: list[dict]) -> None:
    """Print the table and the growth verdict."""
    print(
        f"{'entries':>8}{'KiB':>9}{'envelope ms':>13}"
        f"{'statement ms':>14}{'us/entry':>10}"
    )
    for row in rows:
        print(
            f"{row['entries']:>8}{row['kib']:>9.1f}"
            f"{row['envelope_ms']:>13.3f}{row['statement_ms']:>14.2f}"
            f"{row['us_per_entry']:>10.1f}"
        )
    drift = rows[-1]["us_per_entry"] / rows[0]["us_per_entry"]
    print(
        f"\n  us/entry at {rows[-1]['entries']:,} entries is {drift:.2f}x "
        f"the cost at {rows[0]['entries']:,}. Flat is linear; climbing "
        f"means something rescans what it has already read."
    )


def main() -> int:
    """Run the benchmark and print a table or JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--quick", action="store_true", help="small sizes, as CI runs"
    )
    args = parser.parse_args()
    rows = run(quick=args.quick)
    if args.json:
        json.dump(rows, sys.stdout, indent=1)
        print()
    else:
        render(rows)
    for row in rows:
        if row["transactions"] != row["entries"]:
            print(f"parsed {row['transactions']} of {row['entries']}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
