# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""EBICS 3.0 / 2.5 transport protocol adapter for bankstatementparser."""

from __future__ import annotations

from .client import (
    EbicsClient,
    EbicsConfig,
    EbicsKeyStore,
    EbicsOrderType,
    EbicsResponse,
    fetch_and_parse,
    fetch_statement,
)

__version__ = "0.0.19"
__all__ = [
    "EbicsClient",
    "EbicsConfig",
    "EbicsKeyStore",
    "EbicsOrderType",
    "EbicsResponse",
    "__version__",
    "fetch_and_parse",
    "fetch_statement",
]
