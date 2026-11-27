# Usage

## Configuration

`EbicsConfig(host_id, partner_id, user_id, url, version="H005",
security_medium="0000")` holds the bank's host ID, your partner and user
IDs and the endpoint. `version` is `H005` (EBICS 3.0) or `H004`
(EBICS 2.5) and becomes the request namespace (`urn:org:ebics:H005`).
`url` is stored and never contacted.

`EbicsClient(config, key_store=None)` takes an optional `EbicsKeyStore`
(signature, authentication and encryption key values and the bank's
public key). Without one it uses placeholder values.

## Building requests

- `build_initialization_request("INI")` or `("HIA")` returns an
  `ebicsRequest` document in the initialisation phase with order
  attribute `OZHNN` and the SHA-256 digest of the signature key value.
- `build_download_request(order_type, start_date, end_date)` returns a
  download request (order attribute `DZHNN`) for any `EbicsOrderType`
  or order-type string; a date range is added only when both dates are
  given.

Field values from `EbicsConfig` are inserted without XML escaping, so
pass only trusted IDs.

## Reading responses

`parse_response(xml)` accepts bytes or text and returns an
`EbicsResponse`:

| Field | Taken from |
| :--- | :--- |
| `return_code` | `<ReturnCode>`; empty when the tag is absent or unclosed |
| `report_text` | `<ReportText>` |
| `order_id`, `transaction_id` | `<OrderID>`, `<TransactionID>` |
| `payload` | `<OrderData>`, base64-decoded; the raw text when it is not base64 |
| `is_segment_complete` | `True` for return codes `000000` and `011000` |

`is_success` is `True` only for an explicit `000000`, `011000` or
`011001`; a response with no return code is never a success.

## Parsing statements

`fetch_statement(order_type, start_date, end_date, mock_payload)` parses
the statement in `mock_payload` (bytes or text) with the core
`bankstatementparser` and returns `Transaction` objects with
`source="ebics"`; debit rows (`DBIT`, `D`, `DEBT`) become negative
amounts. Without a payload it returns an empty list. `fetch_and_parse`
returns the same rows as a pandas DataFrame with the columns `date`,
`description`, `amount`, `currency`, `account_id`, `reference` and
`source`. Module-level `fetch_statement(config, ...)` and
`fetch_and_parse(config, ...)` build the client for you.

The order type and dates are accepted for symmetry with the request
builders; parsing does not use them.

## Limits

- No network transport: nothing is sent or received.
- No signing (`A006`), authentication (`X002`) or encryption (`E002`) of
  requests, and no verification or decryption of responses. Real order
  data is compressed and encrypted; this package decodes base64 only.
- No segmented (multi-part) download handling beyond reporting
  `is_segment_complete`.
