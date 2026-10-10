# UBER micro demos

**Twenty-nine DOS demos, each under 9 bytes of x86 assembly: the screen painted by the stack, a program that prints its own machine code, one that reverses your command line, one that shows the state DOS left the CPU in, four that make noise, and three that are two programs in the same eight bytes.**

[![CI](https://github.com/djayuffe/uber-micro-demos/actions/workflows/ci.yml/badge.svg)](https://github.com/djayuffe/uber-micro-demos/actions/workflows/ci.yml)

![Twenty-one of the demos in DOSBox](docs/gallery.jpg)

*Real DOSBox captures. Row 1: STACKMAP, SPECTRUM, STKRAIN, BULLETS. Row 2: STATE, FLUX, WEAVE, EVO1. Row 3: EVO2, SNOW, MIRROR, PSPBACK
(`PSPBACK hello tiny world`). Row 4: KEYSCAN (after a key press), STRIPE, CODEPAL, PSPPAL (the two that recolour the DOS screen and exit).
Row 5: NOISEPAL (one frame of the churn), TALL (80x50), BIG (40x25). Row 6: OVERLAP (the DOS screen corroding) and OVERSUB (random characters).*

None of them sets a video mode, loads a file or allocates memory. They use what DOS hands a `.COM` for
free (`AX = BX = 0`, `SI = 100h`, text mode 3, the BIOS and the PC's hardware) and bend it:

| Preview | Demo | Bytes | What it does |
|---|---|---:|---|
| <img src="docs/thumbs/STACKMAP.jpg" width="120" alt="STACKMAP"> | **STACKMAP** | 7 | the **stack is the screen**, and every cell shows its own address: a map of video memory |
| <img src="docs/thumbs/STKRAIN.jpg" width="120" alt="STKRAIN"> | **STKRAIN** | 8 | the stack is the screen again, and a counter pours down it: a rainbow of every character |
| <img src="docs/thumbs/BULLETS.jpg" width="120" alt="BULLETS"> | **BULLETS** | 7 | infinite **recursion** with the stack on the screen: every `CALL` pushes a return address, and the screen fills with blue bullets |
| <img src="docs/thumbs/STATE.jpg" width="120" alt="STATE"> | **STATE** | 7 | the **machine's start-up state**, painted: `pusha` stacks the eight registers DOS left behind, as a tile that repeats across the screen |
| <img src="docs/thumbs/FLUX.jpg" width="120" alt="FLUX"> | **FLUX** | 8 | STATE with a **second moving column**: `dec cx` makes CX one lower for every tile, so two glyph columns drift |
| <img src="docs/thumbs/WEAVE.jpg" width="120" alt="WEAVE"> | **WEAVE** | 8 | the address map **woven** with SI's start-up value: every other cell is a blank blue one |
| <img src="docs/thumbs/EVO1.jpg" width="120" alt="EVO1"> | **EVO1** | 8 | **found by evolution**: a stack segment that overlaps the text page out of phase, with SI and DI drifting: dense columns of glyphs |
| <img src="docs/thumbs/EVO2.jpg" width="120" alt="EVO2"> | **EVO2** | 8 | EVO1's cousin (another segment, `cmpsb` for `cmpsw`): a blue wall with colourful glyph strips |
| <img src="docs/thumbs/OVERLAP.jpg" width="120" alt="OVERLAP"> | **OVERLAP** | 8 | **two programs in the same bytes**: the `JMP` lands one byte inside the first instruction, so `lds si,[bx+si]` becomes `xor [si],al` / `lodsw` / `out 61h,al`. It feeds memory to the speaker and **corrodes the DOS screen** (the walk crosses the text page). Silent over empty memory. |
| <img src="docs/thumbs/OVERSUB.jpg" width="120" alt="OVERSUB"> | **OVERSUB** | 8 | OVERLAP with `sub` for `xor` (30h becomes 28h, so `lds` loads BP and SI stays put): AL flips ADh, 53h, ADh..., so the speaker toggles on every write, and the screen fills with random characters |
| <img src="docs/thumbs/OVERHEAR.jpg" width="120" alt="OVERHEAR"> | **OVERHEAR** | 8 | OVERLAP with `cmp`: the loop only **reads**, so it sends every word of the walked window (the DOS screen's text included) to the speaker port without disturbing the screen |
| <img src="docs/thumbs/SPECTRUM.jpg" width="120" alt="SPECTRUM"> | **SPECTRUM** | 8 | STACKMAP with the stack **one byte off**: every word straddles two cells, so the colour changes every cell and the glyph every 128: a test card |
| <img src="docs/thumbs/SNOW.jpg" width="120" alt="SNOW"> | **SNOW** | 8 | a **blizzard** of random glyphs: the timer's fast counter, forced into codes 128-255 |
| <img src="docs/thumbs/BREATH.jpg" width="120" alt="BREATH"> | **BREATH** | 7 | the text **cursor pulses**: its shape changes every timer tick |
| <img src="docs/thumbs/STRIPE.jpg" width="120" alt="STRIPE"> | **STRIPE** | 8 | a three-row **colour band** at the cursor, a new colour every timer tick |
| <img src="docs/thumbs/PSPBACK.jpg" width="120" alt="PSPBACK"> | **PSPBACK** | 7 | reads DOS's own **Program Segment Prefix backwards**: `PSPBACK hello tiny world` prints `dlrow ynit olleh` (and the FCBs, parsed from your arguments) |
| <img src="docs/thumbs/MIRROR.jpg" width="120" alt="MIRROR"> | **MIRROR** | 8 | a program that **prints its own machine code**, then exits cleanly |
| <img src="docs/thumbs/BUZZ.jpg" width="120" alt="BUZZ"> | **BUZZ** | 6 | flips the **PC speaker** as fast as the CPU can: a buzz whose pitch is the CPU speed |
| <img src="docs/thumbs/STATIC.jpg" width="120" alt="STATIC"> | **STATIC** | 6 | **white noise**: the timer's fastest-changing bits drive the speaker |
| <img src="docs/thumbs/TICKER.jpg" width="120" alt="TICKER"> | **TICKER** | 6 | a **metronome**: the speaker bits step 1, 2, 3, 0 on every 55 ms tick |
| <img src="docs/thumbs/GEIGER.jpg" width="120" alt="GEIGER"> | **GEIGER** | 7 | a **Geiger counter**: random clicks, 18 a second |
| <img src="docs/thumbs/TYPER.jpg" width="120" alt="TYPER"> | **TYPER** | 7 | a **typewriter**: whatever you press is echoed back |
| <img src="docs/thumbs/KEYSCAN.jpg" width="120" alt="KEYSCAN"> | **KEYSCAN** | 6 | floods the screen with the glyph of the **last keyboard scancode** |
| <img src="docs/thumbs/CODEPAL.jpg" width="120" alt="CODEPAL"> | **CODEPAL** | 8 | the program's **own machine code becomes the screen's palette**, and the colours stay after it exits (the DOS screen turns salmon and green) |
| <img src="docs/thumbs/PSPPAL.jpg" width="120" alt="PSPPAL"> | **PSPPAL** | 7 | **DOS's Program Segment Prefix becomes the palette**, then exit: the screen turns blue, purple and green, machine-dependent colours |
| <img src="docs/thumbs/NOISEPAL.jpg" width="120" alt="NOISEPAL"> | **NOISEPAL** | 8 | a **palette-only** demo: no pixel is touched; the timer's counter is streamed into all 256 DAC colours, so the screen's colours churn |
| <img src="docs/thumbs/MODE3.jpg" width="120" alt="MODE3"> | **MODE3** | 5 | back to **80x25 text** with the default palette: undoes BIG, TALL, CODEPAL and PSPPAL |
| <img src="docs/thumbs/BIG.jpg" width="120" alt="BIG"> | **BIG** | 4 | **40x25** text (`inc ax` / `int 10h`: AX = 1 is a video mode), then exits |
| <img src="docs/thumbs/TALL.jpg" width="120" alt="TALL"> | **TALL** | 6 | **80x50** text (the BIOS reloads the 8x8 font), then exits |

*Previews are real DOSBox 0.74-3 captures of each program. Five demos have nothing to see, so their preview is a plot of what the emulator says they write: BUZZ, STATIC, TICKER and GEIGER show the speaker cone (port 61h) over time (for STATIC and GEIGER the timer counter is modelled as random values), and BREATH shows the cursor-shape value it sets on each tick. TYPER's capture shows DOSBox's synthetic key injection, which types `a` for every key. MODE3 shows the clean 80x25 screen it restores; OVERHEAR leaves the DOS screen untouched, which is the point.*

## Run them

Download the `.COM` files from the [latest release](../../releases/latest) and run one in
[DOSBox](https://www.dosbox.com/) (`mount c .`, `c:`, `STKRAIN.COM`), or build and launch:

```sh
./build.sh                  # NASM: assembles every demo and enforces each size budget
./run-dosbox.sh stkrain   # any of: overlap oversub overhear stackmap spectrum stkrain bullets state flux weave evo1 evo2 snow breath stripe mirror pspback keyscan big tall codepal psppal noisepal mode3 buzz static ticker geiger typer
```

Needs [NASM](https://www.nasm.us/) (macOS: `brew install nasm`, `brew install --cask dosbox`).

**Only MIRROR, PSPBACK, BIG, TALL, CODEPAL, PSPPAL and MODE3 exit; the rest never do** (there is no room for the keyboard check): close DOSBox, or press Ctrl+F9 in it.
**The launcher pins DOSBox to about 3 MIPS** (`cycles=3000` in `DOSBOX.CONF`). These demos have no room for
timing code, so their speed *is* the CPU's speed: at `cycles=max`, STKRAIN, SNOW, BUZZ and STATIC are an
unreadable blur or an inaudible whine. BREATH, TICKER and GEIGER pace themselves with `HLT`.

## Overlapping instructions

![OVERLAP corroding the DOS screen: the clean DOSBox start-up screen, then text breaking up and blue and green blocks spreading](docs/overlap.gif)

*OVERLAP in real DOSBox 0.74-3 at 3000 cycles, 25 frames per second, 16 seconds. It starts on the untouched DOS screen (a 15-second helper program, not part of the release, waited so the recording could begin clean); then the 64 KB memory walk reaches the text page and the screen corrodes. Recorded by screen-capturing the DOSBox window; a small patch where the mouse pointer sat was painted black.*

OVERLAP, OVERSUB and OVERHEAR (idea from a pasted note on the 8-byte `C5 30 04 AD E6 61 EB F9` trick) run the same bytes
twice, decoded two ways. Pass 1 is `lds si,[bx+si]` / `add al,0ADh` / `out 61h,al` / `jmp`; the jump lands on the 30h
inside the first instruction, and from then on the loop is `xor [si],al` / `lodsw` / `out 61h,al` / `jmp`. Two things
the note got wrong, found by running it: DOS enters a `.COM` with `SI = 0100h`, not 0, so `lds` reads the **program's own bytes**
(DS = AD04h, SI = 30C5h), not the PSP; and that window (AD040h-BD03Fh) **includes the B800h text page**, so it is
not harmless in text mode: it scrambles the screen. Over empty memory the XOR version is silent (AL stays ADh),
which is why OVERSUB exists. The trick generalises: `C5 mm` is `lds reg,[bx+si]` and `mm 04` is `op [si],al`, and the eight ALU opcodes 00, 08, ..., 38 are exactly the legal modrm bytes, so one byte picks the operation. Tried in the emulator: `sub` and `sbb` always toggle the speaker, `xor`, `add`, `adc` need data in memory, `or` and `and` collapse to a constant, and `cmp` never writes, which is OVERHEAR. Both are checked in the emulator; the sound itself is unheard, and with no delay the
tone is far above hearing range, so any audible result is aliasing in the audio path.

## Found-memory demos

The most interesting direction at this size is not "fit an effect into 8 bytes" but "let the 8 bytes unlock something already
sitting in the machine". DOS hands a `.COM` a screen full of data, a 256-byte Program Segment Prefix, a stack with a known word on
it, a known set of registers and the BIOS. Several demos here have almost no renderer at all:

- **PSP as data** (PSPBACK, MIRROR): the program reads DOS's own structures. PSPBACK is the only demo in the *wild* category: it needs a
  command line (try `PSPBACK hello tiny world`), because the PSP is where DOS parsed it. Reading *forwards* does not work: the command
  tail ends in a carriage return, and the zeros after it overwrite the text. Backwards, the text lands last.
- **Stack as art** (STACKMAP, STKRAIN, BULLETS, SPECTRUM): the stack pointer is the cursor, and the screen is the stack.
- **The environment as the texture** (STATE): nothing is initialised on purpose. `pusha` paints whatever DOS left in `DX` (the segment),
  `BP`, `CX`, `SI`, `DI`. A different DOS, or a different PC, paints a different screen: the demo has editions. (Entry state in DOSBox 0.74:
  `AX=0 BX=0 CX=00FF DX=0192 SI=0100 DI=FFFE BP=091C SP=FFFE`, all four segments `0192`, flags `7202`; the DX and flags are one of the
  things that vary.)
- **Hardware as the program** (BIG, TALL, BREATH, STRIPE, the speaker demos): one BIOS or port call does all the work.
- **Demos that outlive the program** (CODEPAL, PSPPAL, BIG, TALL): the program spends a few microseconds configuring the VGA and exits;
  the hardware keeps the effect. CODEPAL and PSPPAL call BIOS "load DAC registers" with `ES:DX` pointing at *memory that already exists*: the program's
  own bytes, or the PSP. Nothing is drawn, yet the whole DOS screen changes colour. (`MODE3` puts it back.) PSPPAL's colours are DOS's: the first
  PSP bytes are `CD 20` and the top-of-memory segment, so a different DOS gives different colours.
- **Palette-only** (NOISEPAL): pixels are never touched. Whatever is on the screen is recoloured, 70 times a second, by the timer. **It flashes
  rapidly through random colours: do not run it if you are sensitive to flicker.** The same goes, more mildly, for STRIPE and BREATH.

**Rules of the game.** *Strict 8*: exactly 8 bytes or fewer in the `.COM`, no payload, no data file, an ordinary launch with no
arguments. Every demo here is strict except PSPBACK, which is *wild* (it reads your command line). KEYSCAN and TYPER want keys.

**Found by evolution** (EVO1, EVO2). A small genetic algorithm: genomes are 8 raw bytes; each is run in the emulated CPU for 90,000
instructions with a "teletype" standing in for `int 29h`, and the screen is sampled at three moments. Fitness rewards *structure* (distinct
cells on the screen), *change over time* (a fraction of cells that changes between samples, neither frozen nor all noise), and *colour variety*, and
punishes anything that crashes, exits or blocks. Mutation (byte, bit, insert, delete, swap) and crossover, seeded with the demos here plus random
variants; 4 runs of 40 generations of 60 genomes, about 240 distinct programs scored. Honest result: it did **not** invent a new technique. It refined the
seed it was given (STATE with a moving column): the whole top of the table was one family, `push imm16 / pop ss / pusha / cmps? / jmp`. The two things it
found that I had not tried: (1) the stack segment need not be `B800h`: `B0FDh` and `B0DDh` put the stack's 64 KB window *across* the text page out of
phase, so the 8-cell register tile no longer lines up with the 80-column screen; (2) `cmpsw` and `cmpsb` are the cheapest way to make SI *and* DI drift at
once (one byte, and a side effect nobody uses). Both are live-verified in DOSBox. Everything it ranked highly was a screen; a fitness that could hear the
speaker or see the palette would need a more complete emulation of the BIOS than I wrote.

**Found by search.** FLUX and WEAVE came from a brute-force run: about 73,000 random 8-byte programs (built from a pool of useful
instructions, each ending in a short backward jump) run in an emulated 16-bit CPU with DOSBox's start-up registers, scored on how rich
the text screen or the printed stream became. About 245 scored at all, and nearly all were variants of programs already here (STACKMAP
with a spare instruction, SNOW and the ASCII table with a different register, STATE with a different counter); the two that
made a clearly different picture live in DOSBox are FLUX (`dec cx` in the `pusha` loop) and WEAVE (`push si` beside `push sp`).

**What I tried and could not use.**
- *CRT-controller abuse* (sweeping the start address or horizontal parameters): it needs 11 bytes for the port, the register index and the
  loop, and wild CRTC values can stress a real monitor, so I did not ship it.
- *BIOS-ROM hallucination*: DOSBox's BIOS is host-side callbacks, not 8086 code, so there are no accidental instruction streams to find.
  It would have to be hunted on a real BIOS dump.
- *Self-walking opcodes*: a program that increments its own `jmp` displacement lands mid-instruction on the second iteration; in the
  emulator the mis-decoded bytes printed one character and then ended the program. Not an image.
- *Text-mode scroll feedback*: the BIOS scroll needs a window in `CX`/`DX`, and the entry state (`CX = 00FF`) is an empty window.
- *Keyboard LEDs as pixels*: the controller needs an acknowledgement between the command byte and the data byte, and nothing here can show whether it works.
- *DOSBox crashes*: a stack-art variant that pushed `ss` and `sp` alternately closed DOSBox outright; I dropped it.

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

**EVO1** and **EVO2**: `push 0B0FDh` / `pop ss` (or `0B0DDh`) sets a stack whose 64 KB window starts a little below the text page and runs across it, so
`pusha`'s 16-byte tiles land out of phase with the screen's 160-byte rows and each row's columns shift; `cmpsw` (or `cmpsb`) then compares `[SI]` with `[ES:DI]`
and advances both pointers, so the SI and DI cells of each tile count up instead of staying constant. Nothing was designed.

**FLUX** is STATE with `dec cx` in the loop: CX is one lower for each tile pushed, so its column drifts as well as the SP column. **WEAVE**
is `push sp` / `push si`: DOS gives `SI = 0100h`, a blank cell with a blue attribute, so it alternates with the address map.

**CODEPAL, PSPPAL**: BIOS `INT 10h` AX = 1012h loads `CX` DAC colour registers, starting at `BX`, from the 3-byte entries at `ES:DX`.
DOS leaves `BX = 0` and `CX = 00FFh`, so one call recolours 255 colours; each is three bytes (red, green, blue) of which the DAC keeps six
bits. CODEPAL points `DX` at itself (`mov dx,si`: DOS gives `SI = 0100h`), so colour 0, the background, is its own first three bytes
`B8 12 10`: a salmon red, and colour 1 is `89 F2 CD`. The rest of the table is zeros, so most colours go black. PSPPAL needs one byte fewer: `cwd`
makes `DX = 0` (AX is positive), which is the start of the PSP, so colour 0 is `CD 20 FF` (light blue) and colour 1 is the next three bytes.

**NOISEPAL**: the DAC data port is `3C9h`; after a mode set the write index is 0 and then auto-increments through all 256 colours, three bytes
each. `in al,40h` / `out dx,al` in a loop streams the timer counter in, so every colour (the background, the text, everything) is replaced by random
values over and over, and DOSBox redraws the unchanged screen with each new palette.

**MODE3**: `mov al,3` (AX = 0 at entry) / `int 10h`: set mode 3, which also reloads the default palette.

**STATE**: `pusha` is one byte that pushes AX, CX, DX, BX, SP, BP, SI, DI. With the stack on the screen, those eight words become an
8-cell tile, repeated down the whole page; the SP cell is the only one that changes (it counts down by 16 each time), so it reads as
a drifting glyph column. The other seven cells are the start-up registers, as DOS left them.

**PSPBACK**: `std` makes `lodsb` walk downwards from `SI = 0100h`, so it reads the PSP backwards: first the zeros after the command
tail, then the carriage return (which sends the cursor home), then the command line reversed, then the two parsed FCBs (your first two
arguments, upper-cased and space-padded, also reversed), then the header. `loop` (with `CX = 00FFh`) stops after 255 bytes and `ret`
returns to the PSP's `INT 20h`.

**KEYSCAN**: `in al,60h` reads the keyboard controller's last byte (the make code when a key goes down, the make code plus 80h when it
comes up) and `int 29h` prints it, over and over.

**BIG** and **TALL** are the BIOS video functions with the registers DOS provides: AX = 0 at entry, so `inc ax` is "set mode 1" (40x25),
and `mov ax,1112h` is "load the 8x8 font", which makes the screen 80x50. Both then `ret` to the PSP's `INT 20h`.

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
address; SPECTRUM's colour and glyph bytes are the low and high bytes of the cell address; MIRROR prints exactly its own bytes and exits; STRIPE writes 255 blanks with a counting attribute once per tick; STATE paints the eight start-up registers as a repeating tile; PSPBACK prints the PSP in reverse (including `dlrow ynit olleh`); BIG and TALL make one BIOS call each and exit; KEYSCAN prints the keyboard port; STKRAIN's hold consecutive counter values; BULLETS fills the screen with `0107h`; SNOW prints the counter it
read, with bit 7 forced on; BREATH sets the cursor shape once per tick, counting up; BUZZ writes 2, 0, 2, 0, ...;
STATIC and GEIGER write exactly the counter they just read (all four gate/cone combinations occur, GEIGER once per
tick); TICKER steps the bits once per tick; TYPER echoes the keys it is given; OVERLAP, OVERSUB and OVERHEAR decode as two programs, drive the speaker port from memory, and (OVERHEAR) never write. CI runs it on every push; a
`vX.Y.Z` tag publishes a release.

**Run live in DOSBox**: OVERLAP and OVERSUB (captured above; OVERHEAR runs and leaves the screen untouched), STACKMAP, SPECTRUM, STKRAIN, BULLETS, SNOW and MIRROR (captured above), STRIPE (the band changes colour), BREATH (the cursor visibly changes
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
