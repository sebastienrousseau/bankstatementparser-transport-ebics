# Examples for bankstatementparser-transport-ebics

Runnable scripts, each run in CI (`for f in examples/*.py`) and by
`tests/test_regression_examples.py`. They read the fixtures in
[`data/`](data/) and open no network connection.

- `01_basic_usage.py`: builds an INI and a C53 download request, then
  parses a C53 download response (return code, IDs, order data).
- `02_advanced_workflow.py`: parses the statement in that response into
  `Transaction` objects with `fetch_statement` and into a pandas
  DataFrame with `fetch_and_parse`.

`data/c53_download_response.xml` carries its statement as plain
base64; a real bank compresses and encrypts order data, which this
package does not undo.
