# UBER micro demos

**Thirteen DOS demos, each under 9 bytes of x86 assembly: the screen painted by the stack, a program that prints itself, a blizzard of glyphs, a pulsing cursor, and four that make noise.**

[![CI](https://github.com/djayuffe/uber-micro-demos/actions/workflows/ci.yml/badge.svg)](https://github.com/djayuffe/uber-micro-demos/actions/workflows/ci.yml)

![Six of the demos in DOSBox: STACKMAP, SPECTRUM, STKRAIN, BULLETS, SNOW and MIRROR](docs/gallery.jpg)

*Real DOSBox captures. Top: STACKMAP, SPECTRUM, STKRAIN. Bottom: BULLETS, SNOW, MIRROR (the line under the command, which is
the program's own machine code). The moving blue cell in STKRAIN and BULLETS is the stack pointer writing the screen.*

None of them sets a video mode, loads a file or allocates memory. They use what DOS hands a `.COM` for
free (`AX = BX = 0`, `SI = 100h`, text mode 3, the BIOS and the PC's hardware) and bend it:

| Demo | Bytes | What it does |
|---|---|---|
| **STACKMAP** | 7 | the **stack is the screen**, and every cell shows its own address: a map of video memory |
| **STKRAIN** | 8 | the stack is the screen again, and a counter pours down it: a rainbow of every character |
| **BULLETS** | 7 | infinite **recursion** with the stack on the screen: every `CALL` pushes a return address, and the screen fills with blue bullets |
| **SPECTRUM** | 8 | STACKMAP with the stack **one byte off**: every word straddles two cells, so the colour changes every cell and the glyph every 128: a test card |
| **SNOW** | 8 | a **blizzard** of random glyphs: the timer's fast counter, forced into codes 128-255 |
| **BREATH** | 7 | the text **cursor pulses**: its shape changes every timer tick |
| **STRIPE** | 8 | a three-row **colour band** at the cursor, a new colour every timer tick |
| **MIRROR** | 8 | a program that **prints its own machine code**, then exits cleanly |
| **BUZZ** | 6 | flips the **PC speaker** as fast as the CPU can: a buzz whose pitch is the CPU speed |
| **STATIC** | 6 | **white noise**: the timer's fastest-changing bits drive the speaker |
| **TICKER** | 6 | a **metronome**: the speaker bits step 1, 2, 3, 0 on every 55 ms tick |
| **GEIGER** | 7 | a **Geiger counter**: random clicks, 18 a second |
| **TYPER** | 7 | a **typewriter**: whatever you press is echoed back |

## Run them

Download the `.COM` files from the [latest release](../../releases/latest) and run one in
[DOSBox](https://www.dosbox.com/) (`mount c .`, `c:`, `STKRAIN.COM`), or build and launch:

```sh
./build.sh                  # NASM: assembles all ten and enforces each size budget
./run-dosbox.sh stkrain   # any of: stackmap spectrum stkrain bullets snow breath stripe mirror buzz static ticker geiger typer
```

Needs [NASM](https://www.nasm.us/) (macOS: `brew install nasm`, `brew install --cask dosbox`).

**All but MIRROR never exit** (there is no room for the keyboard check): close DOSBox, or press Ctrl+F9 in it.
**The launcher pins DOSBox to about 3 MIPS** (`cycles=3000` in `DOSBOX.CONF`). These demos have no room for
timing code, so their speed *is* the CPU's speed: at `cycles=max`, STKRAIN, SNOW, BUZZ and STATIC are an
unreadable blur or an inaudible whine. BREATH, TICKER and GEIGER pace themselves with `HLT`.

## How they work

**The stack as a screen** (STACKMAP, STKRAIN, BULLETS). Text-mode video memory is at `B800:0000`, and
`push 0B800h` / `pop ss` (4 bytes) puts the stack there. After that every `PUSH` and `CALL` is a write to the
screen, and as `SP` counts down and wraps around the 64 KB segment it walks across the whole text page. No
`ES`, no `STOSW`, no pointer: the CPU's stack pointer is the cursor.

- **STACKMAP**: `push sp` stores the stack pointer, which is also the address being written, so each cell holds
  its own address: the character is the low byte (so each row is a ramp of 80 even codes, starting 160 codes
  higher than the row above, modulo 256) and the colour is the high byte (it steps once every 128 cells,
  down the screen).
- **STKRAIN**: `inc ax` / `push ax` writes a counter; character = low byte, colour = high byte.
- **BULLETS**: `call` to itself. The return address `0107h` is pushed over and over: character `07h` (a bullet),
  colour `01h` (blue).

**SPECTRUM**: STACKMAP plus one `dec sp`. With `SP` odd, each pushed word lands across two cells: its low byte (a value
that changes every cell) becomes a *colour attribute*, and its high byte (it changes every 128 cells) the *glyph* of the
next cell. The roles of the two bytes swap, and the address map becomes a wall of colour with a new glyph every row.

**MIRROR**: DOS function 9 prints the `$`-terminated string at `DS:DX`. `mov dx,si` points it at the program itself
(DOS gives `SI = 0100h`), and the eighth byte of the file is the `$`, so it prints its own machine code (`B4 09 89 F2 CD
21 C3`, as `┤`, a tab, `ë≥═!├`) and then `ret`s: the word at the top of the stack is 0, which is the PSP's `INT 20h`.
It is the only demo that exits.

**STRIPE**: BIOS `INT 10h` AH = 9 writes character `AL` with attribute `BL` `CX` times without moving the cursor.
`AL = 0` is a blank, `CX = 00FFh` is 255 cells (three rows), and `inc bx` plus a `HLT` give a new colour every tick.

**SNOW**: `in al,40h` reads the timer's counter (it changes every 0.84 us, so it is a free random number), `or al,80h`
forces it into 128-255 so there are no control codes to disturb the screen, and `int 29h` ("DOS fast console
output") prints it. (An earlier demo, XRAY, dumped low memory the same way, and went blank in real DOSBox:
that memory is mostly zeros, and the odd stray byte can switch DOSBox's ANSI emulation to black-on-black text.)

**BREATH**: BIOS `INT 10h` AH = 1 sets the cursor shape from `CX` (start line, end line); `inc cx` and a `HLT`
(sleep until the next 18.2 Hz tick) animate it. AH = 1 costs one byte: DOS starts a `.COM` with `SI = 0100h`, so
`xchg ax,si` makes `AX = 0100h`.

**The speaker** (BUZZ, STATIC, TICKER, GEIGER). Port `61h` bit 1 is the speaker cone and bit 0 gates timer 2.
BUZZ is `xor al,2` / `out 61h,al` in a loop (`AL` is 0 at entry, so it writes 2, 0, 2, 0, ...). STATIC and GEIGER write the timer's counter (`in al,40h`, which changes every
0.84 us) straight to port `61h`, so its low bits are a free random number generator: STATIC at full speed, GEIGER
held for one tick between writes. TICKER counts through the bit patterns once per tick.

**TYPER**: BIOS `INT 16h` with `AH = 0` blocks for a key and returns it in `AL`; `INT 29h` prints it; `cbw` (one byte) sign-extends `AL`
into `AX`, so `AH` is 0 again for the next wait (ASCII keys are below 128, and function keys return `AL = 0`).

## Testing

`tests/run_tests.sh` runs every binary in an emulated 16-bit CPU (Unicorn), entered the way DOS enters a
`.COM` (`AX = BX = 0`, `CX = 00FFh`, `SI = 0100h`, `DI = SP = FFFEh`), with the BIOS keyboard, the timer
counter and the speaker port emulated. It checks that each is under 9 bytes and within its budget, never touches
memory outside video memory and its own segment, and then its behaviour: STACKMAP's cells each hold their own
address; SPECTRUM's colour and glyph bytes are the low and high bytes of the cell address; MIRROR prints exactly its own bytes and exits; STRIPE writes 255 blanks with a counting attribute once per tick; STKRAIN's hold consecutive counter values; BULLETS fills the screen with `0107h`; SNOW prints the counter it
read, with bit 7 forced on; BREATH sets the cursor shape once per tick, counting up; BUZZ writes 2, 0, 2, 0, ...;
STATIC and GEIGER write exactly the counter they just read (all four gate/cone combinations occur, GEIGER once per
tick); TICKER steps the bits once per tick; TYPER echoes the keys it is given. CI runs it on every push; a
`vX.Y.Z` tag publishes a release.

**Run live in DOSBox**: STACKMAP, SPECTRUM, STKRAIN, BULLETS, SNOW and MIRROR (captured above), STRIPE (the band changes colour), BREATH (the cursor visibly changes
shape between frames) and TYPER (it echoes one character per key; DOSBox's synthetic key injection sent them all as
`a`, which is the injection tool, not TYPER). **What nothing here can tell you**: how BUZZ, STATIC, TICKER and
GEIGER *sound* (the tests check the exact port writes, not the audio), or how any of it looks on a real VGA.

## Related

[uber10-dos-demo](https://github.com/djayuffe/uber10-dos-demo) (a 10-byte ASCII scroller),
[uber128-dos-demo](https://github.com/djayuffe/uber128-dos-demo),
[uber256-rotozoomer](https://github.com/djayuffe/uber256-rotozoomer),
[uber256-dos-intro](https://github.com/djayuffe/uber256-dos-intro) and the big one,
[uber40k-dos-demo](https://github.com/djayuffe/uber40k-dos-demo). The index is
[uber-tiny-demos](https://github.com/djayuffe/uber-tiny-demos).

## License

MIT
