# Comparison

Where bankstatementparser-transport-ebics fits next to what a reader
would otherwise reach for. Every cell comes from this repository or the
other project's own PyPI description; nothing here is a measured ranking.

| Project | Talks to the bank | Signing and encryption | Statement parsing | Licence |
| :--- | :---: | :---: | :---: | :--- |
| **bankstatementparser-transport-ebics** | No | No | Yes, via `bankstatementparser` | Apache-2.0 OR MIT |
| [`fintech`](https://pypi.org/project/fintech/) (joonis) | Yes, EBICS 2.4, 2.5 and 3.0 | Yes | Yes, CAMT and MT940 | Free to use but restricted; the unlicensed EBICS module is limited |

## When each fits

- **bankstatementparser-transport-ebics**: you already download
  statements with an EBICS client (or your bank's portal) and want the
  envelopes and statements as data, in the `bankstatementparser`
  `Transaction` model, under an open-source licence.
- **fintech**: you need the live EBICS connection itself, with key
  management, signing and encryption.

The wider family is listed in [The suite](suite.md).
