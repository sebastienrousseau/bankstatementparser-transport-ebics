# Changelog

All notable changes to `bankstatementparser-transport-ebics` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- CI: four pinned actions move to their latest releases:
  codeql-action 4.39.5, markdownlint-cli2-action 25.1.0,
  cosign-installer 4.1.4 and sbom-action 0.24.4.

### Fixed

- The suite consistency check authenticates its GitHub API request
  with the workflow token, so the shared anonymous rate limit no
  longer fails it.

## [0.0.36] - 2026-11-27

In lockstep with the suite's 0.0.36 release.

### Added

- `fuzz/fuzz_parse_response.py`: an Atheris target for
  `EbicsClient.parse_response`, run for two minutes by the CI
  `Fuzz (Atheris)` job. It fails on any exception, on a verdict for a
  response with no return code, and on an inconsistent segment flag.
- `benches/bench_ebics.py`: times `parse_response` and
  `fetch_statement` from 10 to 5,000 statement entries, replacing a
  benchmark that timed an empty loop. CI runs it with `--quick`.
- A user manual built with MkDocs Material (`mkdocs.yml`, `docs/`),
  with usage, architecture, comparison, benchmarks, the supported
  Python policy and an API reference, deployed to GitHub Pages by
  `.github/workflows/docs.yml`. `ARCHITECTURE.md`, `GOVERNANCE.md`,
  `SUPPORT.md` and `CODE_OF_CONDUCT.md` are new.
- A `Makefile`: `make check` runs every local gate; `bench`, `fuzz`,
  `docs`, `demo`, `audit` and `requirements` targets.
- Hashed `requirements/` exports of `poetry.lock`
  (`scripts/export_locked_requirements.py`), installed by every CI job
  with `--require-hashes`; CI fails when they drift from the lock.
- `.github/workflows/security.yml`: `pip-audit` on the runtime, dev,
  docs and fuzz sets on every change and weekly.
- `.github/workflows/scorecard.yml` (OpenSSF Scorecard) and
  `.github/workflows/docs-lint.yml` (README template check and
  markdownlint), issue templates and a pull request template.
- Releases attach cosign signatures (`.sig`, `.pem`), SLSA provenance
  (`.intoto.jsonl`) and CycloneDX and SPDX SBOMs to the GitHub release.
- `.github/demo.gif`, rendered from `.github/demo.tape` by `make demo`.

### Changed

- Requires `bankstatementparser >= 0.0.35` (was `>= 0.0.34`), the
  newest core release on PyPI.
- CI tests on ubuntu, macOS and Windows with CPython 3.10 to 3.14
  (Linux only before), and every action is pinned by commit SHA except
  the SLSA generator, which must be referenced by tag.
- The examples now use the package: they build requests, read a C53
  download response and parse its statement from fixtures in
  `examples/data/`.
- The README follows the portfolio template; the limits that were
  under "Current limitations" are under "When not to use".
- `CONTRIBUTING.md` drops the instruction to install a pre-commit hook
  the repository never had; `SECURITY.md` adds a private-advisory link
  and states what the package does not protect.

### Removed

- `docs/conf.py` and `docs/readme.md`: a Sphinx configuration nothing
  installed or built, and a page that only pointed at the README.

## [0.0.35] - 2026-11-26

Joins the bankstatementparser suite's lockstep release, from 0.0.19
straight to the suite's version, and is the first release published
to PyPI.

### Added

- `.github/workflows/release.yml`: on a `v*.*.*` tag, builds the sdist
  and wheel, checks the tag matches `__version__` and that the release
  highlights and CHANGELOG section exist, publishes to PyPI through
  trusted publishing, and writes the GitHub release notes with
  `scripts/release_notes.py`.
- `.github/workflows/suite-consistency.yml` and
  `scripts/check_suite_consistency.py`: a daily check that every suite
  package published on PyPI, and the website, carry the same version.
- `.github/workflows/pr.yml`: a single-job PR gate (lint, format, type
  check, tests, docstring coverage).
- `.github/dependabot.yml`: weekly pip and grouped GitHub Actions
  updates; the repository had none.
- `tests/test_suite_conformance.py`, the suite's vendored conformance
  checks, and `scripts/verify_versions.py`.
- `scripts/check_complexity.py`, the suite's complexity gate, with
  `scripts/complexity_baseline.json`: per-function ceilings
  (cyclomatic 10, cognitive 15, Halstead 30, 60 lines; 500 lines per
  file), run in CI's lint job. The 5 functions and files already over
  a ceiling are baselined and may not get worse.
- `.github/workflows/codeql.yml`: CodeQL scanning of the workflows and
  the Python sources as an advanced setup, replacing GitHub's default
  setup; the `Analyze (actions)` and `Analyze (python)` check names are
  unchanged.

### Changed

- Requires `bankstatementparser >= 0.0.34` (was `>= 0.0.18`); the lock
  is refreshed, and ruff may now resolve to 0.17.
- CI moves to `actions/checkout@v7` and `actions/setup-python@v7`, adds
  a `Test (all)` check that stands for every leg of the test matrix,
  runs the examples, and installs the built wheel into a clean
  virtualenv and imports it.
- The coverage gate measures branches as well as lines.
- `test_version` reads the expected version from `pyproject.toml`
  instead of restating it.
- README and package description now say what the adapter does: it
  builds EBICS envelopes, reads responses and parses a statement
  payload you supply. It opens no network connection and does no
  signing or encryption; a Current limitations section says so, and
  the Quick start passes a payload.

### Fixed

- `EbicsClient.parse_response` reported a response with no
  `<ReturnCode>` (or an unclosed one) as a success with a complete
  segment. It now starts from an empty code, so `is_success` holds only
  for an explicit success code.
- Branch coverage was 95.08%, not the 100% the 0.0.19 entry claimed:
  tests now cover absent and unclosed response tags and statement rows
  with a missing, null or non-ISO booking date.

## [0.0.19] - 2026-09-01

### Added

- Initial production release of `bankstatementparser-transport-ebics`: EBICS 3.0 & 2.5 Transport Protocol Adapter.
- 100% statement and branch test coverage.
- High-concurrency throughput testing (>10,000 TPS) with sub-second response times.
- Strict type hints (`mypy --strict`) and ruff linting.
- Integration with the core `bankstatementparser` ecosystem.
