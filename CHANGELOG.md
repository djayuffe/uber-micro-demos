# Changelog

Pushing a `vX.Y.Z` tag runs `.github/workflows/release.yml`, which builds, tests and attaches the ten
`.COM` files to a GitHub release using that version's section below.

## [1.0.0] - 2026-10-10

First release: ten demos, each under 9 bytes.

- STACKMAP (7), STACKRAIN (8), BULLETS (7): the stack pointed at the text screen.
- XRAY (7): low memory printed as text.
- BREATH (8): a pulsing cursor.
- BUZZ (8), STATIC (6), TICKER (6), GEIGER (7): the PC speaker.
- TYPER (8): a typewriter.
- `build.sh` enforces a per-demo size budget; `tests/run_tests.sh` runs every binary in an emulated 16-bit CPU;
  CI and tag-driven releases on GitHub Actions.
