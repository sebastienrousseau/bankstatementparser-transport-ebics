# Changelog

All notable changes to `bankstatementparser-transport-ebics` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
