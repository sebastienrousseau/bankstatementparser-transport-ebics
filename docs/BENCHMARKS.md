# Benchmarks

`benches/bench_ebics.py` measures the two steps that run on every C53
download, as the statement grows:

- **envelope**: `parse_response` pulling the return code, IDs and base64
  order data out of the EBICS response;
- **statement**: `fetch_statement` parsing that CAMT.053 order data into
  `Transaction` objects through the core `bankstatementparser`.

Each figure is the best of five runs after one warm-up. Nothing asserts a
threshold: wall-clock is not comparable between machines. CI runs
`python benches/bench_ebics.py --quick` on every operating system and
Python in the test matrix so the benchmark keeps running against the
current API, and fails if a statement loses entries.

## Results

Run with `poetry run python benches/bench_ebics.py` on 2026-11-27:
Apple M1 Pro, macOS 27.2.1, CPython 3.12.16,
bankstatementparser-transport-ebics 0.0.36 with bankstatementparser
0.0.35.

| Entries | Response KiB | Envelope ms | Statement ms | us per entry |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 3.7 | 0.006 | 18.44 | 1844.5 |
| 100 | 31.0 | 0.032 | 24.24 | 242.4 |
| 1,000 | 306.4 | 0.271 | 82.83 | 82.8 |
| 5,000 | 1,540.8 | 1.366 | 349.62 | 69.9 |

Reading the envelope is linear and cheap: about 0.9 ms per MiB of
response. Parsing the statement carries a fixed cost of roughly 18 ms
per call (the temporary file and the core parser's setup), after which
each further entry costs about 67 us (1,000 to 5,000 entries), so the per-entry figure falls as the
statement grows and nothing rescans earlier entries.

Reproduce with `python benches/bench_ebics.py` (add `--json` for
machine-readable output).
