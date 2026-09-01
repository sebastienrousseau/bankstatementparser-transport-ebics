# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Concurrency and stress tests for EBICS transport client."""

import time
from concurrent.futures import ThreadPoolExecutor

from bankstatementparser_transport_ebics import EbicsClient, EbicsConfig

SAMPLE_RESP = """<?xml version="1.0" encoding="UTF-8"?>
<ebicsResponse>
  <header>
    <ReturnCode>000000</ReturnCode>
    <ReportText>OK</ReportText>
    <OrderID>ORD-123</OrderID>
    <TransactionID>TX-999</TransactionID>
  </header>
  <body><DataTransfer/></body>
</ebicsResponse>"""


def test_ebics_concurrency() -> None:
    """Verify EBICS request building and response parsing throughput."""
    config = EbicsConfig("H", "P", "U", "https://bank.com")
    client = EbicsClient(config)

    iterations = 2000
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(client.parse_response, SAMPLE_RESP)
            for _ in range(iterations)
        ]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start

    assert len(results) == iterations
    for resp in results:
        assert resp.is_success
        assert resp.order_id == "ORD-123"
    assert elapsed < 5.0
