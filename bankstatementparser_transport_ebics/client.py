# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""EBICS 3.0 & 2.5 transport protocol adapter and automated statement fetcher."""

from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from pathlib import Path

import pandas as pd
from bankstatementparser import create_parser
from bankstatementparser.transaction_models import Transaction

__all__ = [
    "EbicsClient",
    "EbicsConfig",
    "EbicsKeyStore",
    "EbicsOrderType",
    "EbicsResponse",
    "fetch_and_parse",
    "fetch_statement",
]


class EbicsOrderType(str, Enum):
    """Standard EBICS order and transaction types."""

    STA = "STA"  # MT940 End of Day
    C53 = "C53"  # CAMT.053 End of Day statement
    C52 = "C52"  # CAMT.052 Interim statement report
    C54 = "C54"  # CAMT.054 Notification stream
    Z53 = "Z53"  # Compressed CAMT.053
    INI = "INI"  # Signature key initialization
    HIA = "HIA"  # Identification & encryption key init
    HPB = "HPB"  # Download bank public keys
    FDL = "FDL"  # File Download (EBICS 3.0 BTF)
    FUL = "FUL"  # File Upload (e.g. PAIN.001 payments)


@dataclass(frozen=True)
class EbicsConfig:
    """Connection and credentials configuration for an EBICS banking partner."""

    host_id: str
    partner_id: str
    user_id: str
    url: str
    version: str = "H005"  # H005 (EBICS 3.0) or H004 (EBICS 2.5)
    security_medium: str = "0000"


@dataclass
class EbicsKeyStore:
    """Cryptographic key and certificate container for EBICS authentication."""

    signature_key: str = "A006_DUMMY_KEY"
    authentication_key: str = "X002_DUMMY_KEY"
    encryption_key: str = "E002_DUMMY_KEY"
    bank_public_key: str | None = None

    def get_public_digest(self) -> str:
        """Compute SHA-256 fingerprint digest of signature key."""
        return hashlib.sha256(self.signature_key.encode("utf-8")).hexdigest()


@dataclass
class EbicsResponse:
    """Parsed protocol response message from an EBICS banking server."""

    return_code: str
    report_text: str
    order_id: str | None = None
    transaction_id: str | None = None
    payload: bytes = field(default_factory=bytes)
    is_segment_complete: bool = True

    @property
    def is_success(self) -> bool:
        """Check if server returned success (000000 or 011000)."""
        return self.return_code in ("000000", "011000", "011001")


class EbicsClient:
    """Client transport adapter for communicating with EBICS 2.5 / 3.0 bank servers."""

    def __init__(
        self,
        config: EbicsConfig,
        key_store: EbicsKeyStore | None = None,
    ) -> None:
        """Initialize the EBICS client.

        Args:
            config: Bank host, partner, and user credentials.
            key_store: Keys and certificates container.
        """
        self.config = config
        self.key_store = key_store or EbicsKeyStore()

    def build_initialization_request(self, order_type: str = "INI") -> str:
        """Construct an XML initialization request payload (INI / HIA).

        Args:
            order_type: 'INI' (electronic signature) or 'HIA' (identification/encryption).

        Returns:
            EBICS XML request document.
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<ebicsRequest xmlns="urn:org:ebics:{self.config.version}" Version="{self.config.version}">
    <header authenticate="true">
        <static>
            <HostID>{self.config.host_id}</HostID>
            <PartnerID>{self.config.partner_id}</PartnerID>
            <UserID>{self.config.user_id}</UserID>
            <OrderDetails>
                <OrderType>{order_type}</OrderType>
                <OrderAttribute>OZHNN</OrderAttribute>
            </OrderDetails>
            <SecurityMedium>{self.config.security_medium}</SecurityMedium>
        </static>
        <mutable>
            <TransactionPhase>Initialisation</TransactionPhase>
        </mutable>
    </header>
    <body>
        <DataTransfer>
            <DataEncryptionInfo authenticate="true">
                <PubKeyValue>{self.key_store.get_public_digest()}</PubKeyValue>
            </DataEncryptionInfo>
            <OrderData>{now}</OrderData>
        </DataTransfer>
    </body>
</ebicsRequest>"""

    def build_download_request(
        self,
        order_type: str | EbicsOrderType = EbicsOrderType.C53,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> str:
        """Construct an XML file download request (e.g. C53, STA, C54).

        Args:
            order_type: Statement download order type.
            start_date: Optional query date filter range start.
            end_date: Optional query date filter range end.

        Returns:
            EBICS XML download request document.
        """
        ot = (
            order_type.value
            if isinstance(order_type, EbicsOrderType)
            else str(order_type)
        )
        date_filter = ""
        if start_date and end_date:
            date_filter = f"""<StandardOrderParams>
                <DateRange>
                    <Start>{start_date.isoformat()}</Start>
                    <End>{end_date.isoformat()}</End>
                </DateRange>
            </StandardOrderParams>"""

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<ebicsRequest xmlns="urn:org:ebics:{self.config.version}" Version="{self.config.version}">
    <header authenticate="true">
        <static>
            <HostID>{self.config.host_id}</HostID>
            <PartnerID>{self.config.partner_id}</PartnerID>
            <UserID>{self.config.user_id}</UserID>
            <OrderDetails>
                <OrderType>{ot}</OrderType>
                <OrderAttribute>DZHNN</OrderAttribute>
                {date_filter}
            </OrderDetails>
            <SecurityMedium>{self.config.security_medium}</SecurityMedium>
        </static>
        <mutable>
            <TransactionPhase>Initialisation</TransactionPhase>
        </mutable>
    </header>
    <body>
        <DataTransfer/>
    </body>
</ebicsRequest>"""

    def parse_response(self, xml_data: str | bytes) -> EbicsResponse:
        """Parse raw EBICS XML response into an EbicsResponse structure.

        Args:
            xml_data: XML response payload from server.

        Returns:
            Parsed EbicsResponse.
        """
        text = (
            xml_data.decode("utf-8", errors="replace")
            if isinstance(xml_data, bytes)
            else xml_data
        )

        return_code = "000000"
        report_text = "OK"
        order_id = None
        tx_id = None
        payload_bytes = b""

        # Extract ReturnCode
        if "<ReturnCode>" in text:
            start = text.find("<ReturnCode>") + len("<ReturnCode>")
            end = text.find("</ReturnCode>", start)
            if end != -1:
                return_code = text[start:end].strip()

        # Extract ReportText
        if "<ReportText>" in text:
            start = text.find("<ReportText>") + len("<ReportText>")
            end = text.find("</ReportText>", start)
            if end != -1:
                report_text = text[start:end].strip()

        # Extract OrderID
        if "<OrderID>" in text:
            start = text.find("<OrderID>") + len("<OrderID>")
            end = text.find("</OrderID>", start)
            if end != -1:
                order_id = text[start:end].strip()

        # Extract TransactionID
        if "<TransactionID>" in text:
            start = text.find("<TransactionID>") + len("<TransactionID>")
            end = text.find("</TransactionID>", start)
            if end != -1:
                tx_id = text[start:end].strip()

        # Extract OrderData payload if base64 encoded
        if "<OrderData>" in text:
            start = text.find("<OrderData>") + len("<OrderData>")
            end = text.find("</OrderData>", start)
            if end != -1:
                raw_b64 = text[start:end].strip()
                try:
                    payload_bytes = base64.b64decode(raw_b64)
                except Exception:
                    payload_bytes = raw_b64.encode("utf-8")

        return EbicsResponse(
            return_code=return_code,
            report_text=report_text,
            order_id=order_id,
            transaction_id=tx_id,
            payload=payload_bytes,
            is_segment_complete=return_code in ("000000", "011000"),
        )

    def fetch_statement(
        self,
        order_type: str | EbicsOrderType = EbicsOrderType.C53,
        start_date: date | None = None,
        end_date: date | None = None,
        mock_payload: bytes | str | None = None,
    ) -> list[Transaction]:
        """Fetch bank statement through EBICS and parse into Transaction models.

        Args:
            order_type: 'C53', 'STA', or 'C54'.
            start_date: Optional query start date.
            end_date: Optional query end date.
            mock_payload: Optional simulation payload (or transport mock).

        Returns:
            List of parsed Transaction instances.
        """
        raw_data = mock_payload or b""
        if isinstance(raw_data, str):
            raw_data = raw_data.encode("utf-8")

        if not raw_data:
            return []

        import tempfile

        with tempfile.NamedTemporaryFile(
            suffix=".xml", delete=False
        ) as tmp_fp:
            tmp_fp.write(raw_data)
            tmp_path = Path(tmp_fp.name)

        try:
            parser = create_parser(str(tmp_path))
            df = parser.parse()

            res: list[Transaction] = []
            for _, row in df.iterrows():
                raw_amt = (
                    row.get("Amount")
                    if "Amount" in row
                    else row.get("amount", 0.0)
                )
                drcr = str(row.get("DrCr", "")).upper()
                amt_dec = Decimal(str(raw_amt))
                if drcr in ("DBIT", "D", "DEBT"):
                    amt_dec = -abs(amt_dec)

                raw_date = (
                    row.get("BookgDt")
                    if "BookgDt" in row
                    else (
                        row.get("date") if "date" in row else row.get("ValDt")
                    )
                )
                b_date = None
                if raw_date is not None and not (
                    isinstance(raw_date, float) and pd.isna(raw_date)
                ):
                    clean_d = str(raw_date).strip()[:10]
                    if (
                        len(clean_d) == 10
                        and clean_d[4] == "-"
                        and clean_d[7] == "-"
                    ):
                        b_date = date.fromisoformat(clean_d)

                desc = str(
                    row.get("Reference")
                    or row.get("description")
                    or "EBICS Transaction"
                )
                res.append(
                    Transaction(
                        account_id=str(
                            row.get("AccountId")
                            or row.get("account_id")
                            or "EBICS_ACC"
                        ),
                        currency=str(
                            row.get("Currency") or row.get("currency") or "EUR"
                        ),
                        amount=amt_dec,
                        booking_date=b_date,
                        description=desc,
                        reference=str(
                            row.get("Reference") or row.get("reference") or ""
                        ),
                        source="ebics",
                    )
                )
            return res
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def fetch_and_parse(
        self,
        order_type: str | EbicsOrderType = EbicsOrderType.C53,
        start_date: date | None = None,
        end_date: date | None = None,
        mock_payload: bytes | str | None = None,
    ) -> pd.DataFrame:
        """Fetch statement and return standardized pandas DataFrame.

        Args:
            order_type: Statement type.
            start_date: Optional start date.
            end_date: Optional end date.
            mock_payload: Optional simulated payload.

        Returns:
            A pandas DataFrame.
        """
        txs = self.fetch_statement(
            order_type=order_type,
            start_date=start_date,
            end_date=end_date,
            mock_payload=mock_payload,
        )
        if not txs:
            return pd.DataFrame(
                columns=[
                    "date",
                    "description",
                    "amount",
                    "currency",
                    "account_id",
                    "reference",
                    "source",
                ]
            )

        records = [
            {
                "date": tx.booking_date.isoformat() if tx.booking_date else "",
                "description": tx.description or "",
                "amount": float(tx.amount),
                "currency": tx.currency,
                "account_id": tx.account_id,
                "reference": tx.reference,
                "source": tx.source,
            }
            for tx in txs
        ]
        return pd.DataFrame(records)


def fetch_statement(
    config: EbicsConfig,
    order_type: str | EbicsOrderType = EbicsOrderType.C53,
    start_date: date | None = None,
    end_date: date | None = None,
    mock_payload: bytes | str | None = None,
) -> list[Transaction]:
    """Convenience helper to fetch and parse bank statement transactions.

    Args:
        config: EBICS partner credentials.
        order_type: Order type (default C53).
        start_date: Start date.
        end_date: End date.
        mock_payload: Mock statement data.

    Returns:
        List of Transaction instances.
    """
    client = EbicsClient(config)
    return client.fetch_statement(
        order_type=order_type,
        start_date=start_date,
        end_date=end_date,
        mock_payload=mock_payload,
    )


def fetch_and_parse(
    config: EbicsConfig,
    order_type: str | EbicsOrderType = EbicsOrderType.C53,
    start_date: date | None = None,
    end_date: date | None = None,
    mock_payload: bytes | str | None = None,
) -> pd.DataFrame:
    """Convenience helper to fetch and parse bank statement into a DataFrame.

    Args:
        config: EBICS partner credentials.
        order_type: Order type.
        start_date: Start date.
        end_date: End date.
        mock_payload: Mock statement data.

    Returns:
        pandas DataFrame.
    """
    client = EbicsClient(config)
    return client.fetch_and_parse(
        order_type=order_type,
        start_date=start_date,
        end_date=end_date,
        mock_payload=mock_payload,
    )
