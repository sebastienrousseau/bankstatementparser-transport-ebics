# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR MIT

"""Coverage-guided Atheris fuzz target for the EBICS response parser.

``EbicsClient.parse_response`` reads whatever a bank server (or anything
pretending to be one) sends back: the return code, the report text, the
order and transaction IDs and the base64 order data. It must not raise on
any input, bytes or text. Its verdict must also hold together:

* a response with no ``<ReturnCode>`` is never a success (the 0.0.35 fix:
  an unknown verdict must not read as success);
* ``is_segment_complete`` holds only for ``000000`` or ``011000``;
* the payload is always ``bytes``.

Any exception, or a broken invariant, escapes the target and libFuzzer
records it as a crash.

Run (Linux x86_64, Python 3.12+, ``poetry install --with fuzz``)::

    python fuzz/fuzz_parse_response.py fuzz/corpus -max_total_time=60
"""

from __future__ import annotations

import sys

import atheris

with atheris.instrument_imports():
    from bankstatementparser_transport_ebics import (
        EbicsClient,
        EbicsConfig,
        EbicsResponse,
    )

_CLIENT = EbicsClient(
    EbicsConfig("HOSTID", "PARTNER", "USER", "https://bank.invalid")
)


def _check(text: str, response: EbicsResponse) -> None:
    """Fail unless ``response`` is a coherent reading of ``text``."""
    if not isinstance(response.payload, bytes):
        raise AssertionError("payload is not bytes")
    if "<ReturnCode>" not in text and (
        response.return_code or response.is_success
    ):
        raise AssertionError("no ReturnCode, yet a verdict was reported")
    if response.is_segment_complete and response.return_code not in (
        "000000",
        "011000",
    ):
        raise AssertionError(
            f"segment complete on return code {response.return_code!r}"
        )


def test_one_input(data: bytes) -> None:
    """Parse one fuzz input as raw bytes and as decoded text."""
    text = data.decode("utf-8", errors="replace")
    _check(text, _CLIENT.parse_response(data))
    _check(text, _CLIENT.parse_response(text))


def main() -> None:
    """Hand the target to libFuzzer with the command-line options."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
