<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# bankstatementparser-transport-ebics Architecture

A map of the codebase for contributors. The package is one module of
plain functions and dataclasses; there is no I/O beyond a temporary file
while a statement is parsed.

## The flow

```text
EbicsConfig + EbicsKeyStore
        |
        v
EbicsClient.build_initialization_request()  -> INI/HIA request XML (str)
EbicsClient.build_download_request()        -> C53/STA/... request XML (str)

bank response (bytes or str)  [obtained by another EBICS client]
        |
        v
EbicsClient.parse_response()  -> EbicsResponse(return_code, ..., payload)
        |
        v  payload (CAMT.053 / MT940 / CAMT.054 statement)
EbicsClient.fetch_statement() -> temp file -> bankstatementparser.create_parser()
        |                                        -> pandas DataFrame
        v
list[Transaction]  (fetch_and_parse: pandas DataFrame)
```

## Module map

| Area | Path | Responsibility |
| :--- | :--- | :--- |
| **Client** | `bankstatementparser_transport_ebics/client.py` | `EbicsOrderType`, `EbicsConfig`, `EbicsKeyStore`, `EbicsResponse`, `EbicsClient` and the `fetch_statement` / `fetch_and_parse` helpers |
| **Version** | `bankstatementparser_transport_ebics/__init__.py` | `__version__` and the public re-exports |
| **Tests** | `tests/` | Client behaviour, concurrency and stress, examples, release notes and the suite's vendored conformance checks; 100% line and branch coverage |
| **Fuzzing** | `fuzz/fuzz_parse_response.py`, `fuzz/corpus/` | Atheris target for `parse_response`, run by the CI `Fuzz (Atheris)` job |
| **Benchmarks** | `benches/bench_ebics.py` | Envelope and statement parsing cost by statement size |
| **Examples** | `examples/`, `examples/data/` | Request building, response reading and statement parsing on fixtures |
| **Manual** | `mkdocs.yml`, `docs/` | MkDocs Material user manual and API reference, deployed to GitHub Pages |
| **Release helpers** | `scripts/` | `verify_versions.py`, `release_notes.py`, `export_locked_requirements.py` (hashed exports of `poetry.lock` into `requirements/`), `check_complexity.py`, `check_suite_consistency.py`, `readme-check.sh` |

## Design decisions

- **Data, not transport.** Request building and response reading are
  pure string work, so they can be tested and fuzzed without a bank.
  The network, signing and encryption are not implemented; the README's
  "When not to use" section says so.
- **The core parses statements.** `fetch_statement` hands the payload to
  `bankstatementparser.create_parser` rather than carrying its own CAMT
  or MT940 parser, so the suite has one parser per format.
- **No verdict without a return code.** `parse_response` starts from an
  empty return code, so `is_success` holds only for an explicit success
  code (fixed in 0.0.35; the fuzz target checks it).
- **Substring extraction, not XML parsing,** for responses: it reads the
  first occurrence of each tag and never expands entities.

## CI

`ci.yml` runs the tests on ubuntu, macOS and Windows with CPython 3.10
to 3.14, plus lint, types, Bandit, the complexity baseline, the
examples, the fuzz target and a wheel smoke test. `docs.yml` builds the
manual with `--strict`; `docs-lint.yml` checks the README template and
Markdown; `security.yml` runs `pip-audit`; `codeql.yml` and
`scorecard.yml` scan; `release.yml` publishes a tag.
