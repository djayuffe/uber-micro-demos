# Changelog

Pushing a `vX.Y.Z` tag runs `.github/workflows/release.yml`, which builds, tests and attaches the ten
`.COM` files to a GitHub release using that version's section below.

## [1.5.0] - 2026-10-10

### Added
- **Demos that outlive the program**, from a list of "let the machine do the work" ideas: **CODEPAL** (8 bytes: BIOS load-DAC-registers with the
  program's own bytes as the table), **PSPPAL** (7: the same with DOS's Program Segment Prefix), both of which recolour the DOS screen and exit; and
  **NOISEPAL** (8: a palette-only demo that streams the timer counter into all 256 colours, never touching a pixel; it flashes, with a warning).
- **MODE3** (5 bytes): set 80x25 text, which reloads the default palette: the undo for BIG, TALL, CODEPAL and PSPPAL.
- All verified live in DOSBox; the gallery is sixteen real captures. 24 demos.

## [1.4.0] - 2026-10-10

### Added
- **FLUX** (8 bytes: STATE plus `dec cx`, a second drifting column) and **WEAVE** (8: `push sp` / `push si`), both found by a brute-force
  search of ~73,000 random 8-byte programs in an emulated CPU, then verified live in DOSBox. 20 demos.

## [1.3.0] - 2026-10-10

### Added
- **Found-memory demos**, after a brief on exploiting machine state instead of drawing: **STATE** (7 bytes: `pusha` paints the
  start-up registers as a tile), **PSPBACK** (7: reads DOS's Program Segment Prefix backwards, so `PSPBACK hello tiny world` prints
  `dlrow ynit olleh`; the one *wild* demo, it needs a command line), **KEYSCAN** (6: floods the screen with the last keyboard scancode).
- **BIG** (4 bytes: 40x25 text) and **TALL** (6: 80x50 text), the smallest programs here; both exit cleanly.
- README: a "Found-memory demos" section with the strict/wild rules, the DOSBox entry state, and what was tried and not shipped.
- All five checked live in DOSBox; the gallery is now twelve real captures.

## [1.2.0] - 2026-10-10

### Added
- **SPECTRUM** (8 bytes): STACKMAP with `dec sp`, so every pushed word straddles two screen cells and the address map
  becomes a wall of colour.
- **MIRROR** (8 bytes): prints its own machine code with DOS function 9 (the eighth byte of the file is the `$`) and exits
  cleanly. The only demo that does.
- **STRIPE** (8 bytes): a three-row colour band, a new colour every timer tick (BIOS write-attribute with `CX = 255`).
- All three checked live in DOSBox; the README gallery now shows six real captures.

## [1.1.0] - 2026-10-10

### Changed
- **Three demos shrunk**: BREATH 8 -> **7** bytes (`xchg ax,si` gives `AH = 1` from DOS's `SI = 0100h`), BUZZ 8 -> **6**
  (`xor al,2` / `out 61h,al`: the `in` was only preserving bits nobody needs), TYPER 8 -> **7** (`cbw` clears `AH`
  in one byte instead of `xor ah,ah` in two). The size budgets are tightened to match.
- Checked live in DOSBox: BREATH's cursor changes shape (so `SI = 0100h` holds there) and TYPER echoes one
  character per key.

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
