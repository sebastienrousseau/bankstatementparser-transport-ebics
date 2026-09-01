# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Tests for EBICS 3.0 / 2.5 Transport Protocol Adapter."""

from __future__ import annotations

import base64
from datetime import date
from decimal import Decimal

import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

from bankstatementparser_transport_ebics import (
    EbicsClient,
    EbicsConfig,
    EbicsKeyStore,
    EbicsOrderType,
    EbicsResponse,
    __version__,
    fetch_and_parse,
    fetch_statement,
)


def _sample_camt053_xml() -> str:
    """Return a valid minimal CAMT.053 statement with credit and debit entries."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
  <BkToCstmrStmt>
    <GrpHdr>
      <MsgId>MSG-EBICS-2026-001</MsgId>
    </GrpHdr>
    <Stmt>
      <Id>STMT-001</Id>
      <Acct>
        <Id>
          <IBAN>FR7630006000011234567890189</IBAN>
        </Id>
        <Ccy>EUR</Ccy>
      </Acct>
      <Bal>
        <Tp><CdOrPrtry><Cd>OPBD</Cd></CdOrPrtry></Tp>
        <Amt Ccy="EUR">1000.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt><Dt>2026-01-01</Dt></Dt>
      </Bal>
      <Ntry>
        <Amt Ccy="EUR">250.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <BookgDt><Dt>2026-01-15</Dt></BookgDt>
        <NtryDtls>
          <TxDtls>
            <Refs><EndToEndId>E2E-001</EndToEndId></Refs>
            <RmtInf><Ustrd>Invoice 1024</Ustrd></RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
      <Ntry>
        <Amt Ccy="EUR">50.00</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <BookgDt><Dt>2026-01-16</Dt></BookgDt>
        <NtryDtls>
          <TxDtls>
            <Refs><EndToEndId>E2E-002</EndToEndId></Refs>
            <RmtInf><Ustrd>Bank Fee</Ustrd></RmtInf>
          </TxDtls>
        </NtryDtls>
      </Ntry>
      <Bal>
        <Tp><CdOrPrtry><Cd>CLBD</Cd></CdOrPrtry></Tp>
        <Amt Ccy="EUR">1200.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt><Dt>2026-01-31</Dt></Dt>
      </Bal>
    </Stmt>
  </BkToCstmrStmt>
</Document>
"""


def test_version() -> None:
    """Verifies that version is exposed and semantic."""
    assert __version__ == "0.0.1"


def test_ebics_keystore_digest() -> None:
    """Tests public key digest generation."""
    store = EbicsKeyStore(signature_key="SECRET_A006_KEY")
    digest = store.get_public_digest()
    assert isinstance(digest, str)
    assert len(digest) == 64


def test_build_initialization_request() -> None:
    """Tests building INI and HIA request XML."""
    config = EbicsConfig(
        host_id="EBICSBNK1",
        partner_id="PARTNER99",
        user_id="USER01",
        url="https://ebics.bank.com/ebics",
        version="H005",
    )
    client = EbicsClient(config)

    req_ini = client.build_initialization_request("INI")
    assert "<OrderType>INI</OrderType>" in req_ini
    assert "<HostID>EBICSBNK1</HostID>" in req_ini
    assert "<PartnerID>PARTNER99</PartnerID>" in req_ini
    assert "<UserID>USER01</UserID>" in req_ini

    req_hia = client.build_initialization_request("HIA")
    assert "<OrderType>HIA</OrderType>" in req_hia


def test_build_download_request() -> None:
    """Tests building download request XML with and without date bounds."""
    config = EbicsConfig(
        host_id="EBICSBNK1",
        partner_id="PARTNER99",
        user_id="USER01",
        url="https://ebics.bank.com/ebics",
    )
    client = EbicsClient(config)

    req1 = client.build_download_request(EbicsOrderType.C53)
    assert "<OrderType>C53</OrderType>" in req1

    req2 = client.build_download_request(
        "STA",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )
    assert "<OrderType>STA</OrderType>" in req2
    assert "<Start>2026-01-01</Start>" in req2
    assert "<End>2026-01-31</End>" in req2


def test_parse_response_xml() -> None:
    """Tests parsing server XML response."""
    config = EbicsConfig(
        host_id="EBICSBNK1",
        partner_id="PARTNER99",
        user_id="USER01",
        url="https://ebics.bank.com/ebics",
    )
    client = EbicsClient(config)

    payload_b64 = base64.b64encode(b"STATEMENT_DATA").decode("ascii")
    resp_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ebicsResponse>
    <header>
        <ReturnCode>000000</ReturnCode>
        <ReportText>[EBICS_OK] Processing completed successfully.</ReportText>
        <OrderID>ORD12345</OrderID>
        <TransactionID>TX998877</TransactionID>
    </header>
    <body>
        <OrderData>{payload_b64}</OrderData>
    </body>
</ebicsResponse>"""

    resp = client.parse_response(resp_xml.encode("utf-8"))
    assert isinstance(resp, EbicsResponse)
    assert resp.is_success
    assert resp.return_code == "000000"
    assert resp.order_id == "ORD12345"
    assert resp.transaction_id == "TX998877"
    assert resp.payload == b"STATEMENT_DATA"
    assert resp.is_segment_complete


def test_parse_response_raw_order_data() -> None:
    """Tests parsing non-base64 order data fallback."""
    client = EbicsClient(EbicsConfig("H", "P", "U", "https://bank.com"))
    raw_xml = """<ebicsResponse>
        <ReturnCode>091008</ReturnCode>
        <ReportText>Transaction unknown</ReportText>
        <OrderData>plain_text_order_data</OrderData>
    </ebicsResponse>"""
    resp = client.parse_response(raw_xml)
    assert not resp.is_success
    assert resp.return_code == "091008"
    assert resp.payload == b"plain_text_order_data"


def test_fetch_statement_and_parse() -> None:
    """Tests fetch_statement and fetch_and_parse with CAMT.053 payload."""
    config = EbicsConfig(
        host_id="EBICSBNK1",
        partner_id="PARTNER99",
        user_id="USER01",
        url="https://ebics.bank.com/ebics",
    )

    camt_xml = _sample_camt053_xml()

    # 1. Fetch statement
    txs = fetch_statement(config, mock_payload=camt_xml)
    assert len(txs) == 2
    assert txs[0].amount == Decimal("250.00")
    assert txs[0].currency == "EUR"
    assert txs[0].booking_date == date(2026, 1, 15)
    assert txs[1].amount == Decimal("-50.00")

    # 2. Fetch and parse into DataFrame
    df = fetch_and_parse(config, mock_payload=camt_xml)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "amount" in df.columns
    assert "date" in df.columns

    # 3. Empty payload
    empty_txs = fetch_statement(config, mock_payload=b"")
    assert empty_txs == []
    empty_df = fetch_and_parse(config, mock_payload=b"")
    assert len(empty_df) == 0


@given(
    code=st.sampled_from(["000000", "011000", "011001", "091008", "091005"]),
    msg=st.text(min_size=1, max_size=30).filter(
        lambda s: "<" not in s and ">" not in s and bool(s.strip())
    ),
)
def test_fuzz_ebics_response(code: str, msg: str) -> None:
    """Property-based fuzzing of EBICS response parser."""
    clean_msg = msg.strip()
    client = EbicsClient(EbicsConfig("H", "P", "U", "https://bank.com"))
    xml = f"<ebicsResponse><ReturnCode>{code}</ReturnCode><ReportText>{clean_msg}</ReportText></ebicsResponse>"
    resp = client.parse_response(xml)
    assert resp.return_code == code
    assert resp.report_text == clean_msg
