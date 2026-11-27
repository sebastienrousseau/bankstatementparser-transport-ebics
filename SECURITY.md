# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

Fixes land on the latest `0.0.x` release; there are no back-ported
branches.

## Reporting a Vulnerability

If you discover a security vulnerability in
`bankstatementparser-transport-ebics`, report it privately: open a
[private security advisory](https://github.com/sebastienrousseau/bankstatementparser-transport-ebics/security/advisories/new)
on GitHub or email **<sebastian.rousseau@gmail.com>**. Do not open a
public issue.

Please include a description, steps to reproduce (a minimal request or
response is ideal, with account data redacted), the impact you see and
any fix you suggest.

## What this package does and does not protect

`bankstatementparser-transport-ebics` builds EBICS request XML, reads
EBICS response XML and parses a statement payload you hand it. Know its
limits before you rely on it:

- **No network.** It opens no connection; `EbicsConfig.url` is stored
  and never contacted.
- **No signing, authentication or encryption.** Requests are not signed
  (A006), authenticated (X002) or encrypted (E002), and responses are
  not verified or decrypted. `EbicsKeyStore` holds key values only; the
  INI/HIA request carries a SHA-256 digest of the signature key value.
- **Request XML is built by string formatting** from your
  `EbicsConfig` values without escaping, so pass only trusted IDs.
- **Response parsing** is substring extraction, not an XML parser: no
  entity expansion, no external entity resolution. It is fuzzed with
  Atheris in CI (`fuzz/fuzz_parse_response.py`).
- **Statement payloads** are written to a temporary file, parsed by the
  core `bankstatementparser` and deleted afterwards; XML handling is the
  core parser's.

## Continuous checks

CodeQL, Bandit, `pip-audit` against the locked dependency sets, and the
Atheris fuzz target run on every pull request; OpenSSF Scorecard runs
weekly and on every push to `main`.
