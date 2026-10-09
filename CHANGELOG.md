# Changelog

Pushing a `vX.Y.Z` tag runs `.github/workflows/release.yml`, which builds, tests and attaches the ten
`.COM` files to a GitHub release using that version's section below.

## [1.0.1] - 2026-10-10

### Fixed
- **`STACKRAIN.COM` could not be run**: DOS file names are 8.3, and `STACKRAIN` is 9 letters, so DOSBox
  answered "Illegal command". Renamed to **`STKRAIN.COM`** (a build check now rejects names over 8 letters).
- **XRAY** went blank in real DOSBox (low memory is mostly zeros, and a stray byte can switch the ANSI
  emulation to black-on-black), though its emulator test passed against a synthetic pattern. Replaced by **SNOW**
  (8 bytes): a blizzard of random glyphs, verified live.
- The README gallery is now real DOSBox captures instead of emulator renders.

## [1.0.0] - 2026-10-10

First release: ten demos, each under 9 bytes.

- STACKMAP (7), STKRAIN (8), BULLETS (7): the stack pointed at the text screen.
- XRAY (7): low memory printed as text (replaced in 1.0.1).
- BREATH (8): a pulsing cursor.
- BUZZ (8), STATIC (6), TICKER (6), GEIGER (7): the PC speaker.
- TYPER (8): a typewriter.
- `build.sh` enforces a per-demo size budget; `tests/run_tests.sh` runs every binary in an emulated 16-bit CPU;
  CI and tag-driven releases on GitHub Actions.
