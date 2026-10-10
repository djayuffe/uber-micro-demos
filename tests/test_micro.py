#!/usr/bin/env python3
"""Run each micro demo in an emulated 16-bit CPU (Unicorn), entered the way DOS enters a .COM
(AX = BX = 0, CX = 00FFh, SI = 0100h, DI = SP = FFFEh), and check what it does to the hardware."""
import pathlib, sys
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INSN, UC_HOOK_INTR, UC_HOOK_MEM_UNMAPPED, UC_HOOK_CODE
from unicorn.x86_const import *

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEG = 0x1000
LIN = SEG << 4
fails = []

def check(ok, msg):
    print(("  PASS  " if ok else "  FAIL  ") + msg)
    if not ok: fails.append(msg)

class Run:
    def __init__(self, name, hlt_as_tick=False, port61=0, pit_step=13):
        self.com = (ROOT / name).read_bytes()
        uc = self.uc = Uc(UC_ARCH_X86, UC_MODE_16)
        uc.mem_map(0, 0x10000)                       # segment 0: interrupt vectors, BIOS data
        uc.mem_map(LIN, 0x10000)                     # the program's segment
        uc.mem_map(0xA0000, 0x30000)                 # video memory incl. the B800h text page and the stack wrap
        for i in range(0x100, 0x400): uc.mem_write(i, bytes([i & 255]))   # recognisable low memory
        uc.mem_write(LIN + 0x100, self.com)
        uc.mem_write(LIN, b"\xCD\x20")
        for r in (UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS): uc.reg_write(r, SEG)
        uc.reg_write(UC_X86_REG_SP, 0xFFFE); uc.reg_write(UC_X86_REG_FLAGS, 0x202)
        uc.reg_write(UC_X86_REG_AX, 0); uc.reg_write(UC_X86_REG_BX, 0)
        uc.reg_write(UC_X86_REG_CX, 0xFF); uc.reg_write(UC_X86_REG_SI, 0x100); uc.reg_write(UC_X86_REG_DI, 0xFFFE)
        uc.reg_write(UC_X86_REG_DX, SEG); uc.reg_write(UC_X86_REG_BP, 0x091C)      # as DOSBox leaves them
        self.outs, self.ints, self.chars, self.unmapped, self.ticks = [], [], [], [], 0
        self.p61, self.pit, self.pit_step = port61, 0, pit_step
        self.p60 = 0
        self.tick_hook = []
        self.keys = []
        self.dos_strings, self.exited, self.int10_dx = [], False, []
        if hlt_as_tick and self.com and 0xF4 in self.com:
            for off, b in enumerate(self.com):
                if b == 0xF4: uc.mem_write(LIN + 0x100 + off, b"\x90"); self.hlt_at = LIN + 0x100 + off
            uc.hook_add(UC_HOOK_CODE, self.on_tick, None, self.hlt_at, self.hlt_at)
        uc.hook_add(UC_HOOK_INSN, self.on_in, None, 1, 0, UC_X86_INS_IN)
        uc.hook_add(UC_HOOK_INSN, self.on_out, None, 1, 0, UC_X86_INS_OUT)
        uc.hook_add(UC_HOOK_INTR, self.on_intr)
        uc.hook_add(UC_HOOK_MEM_UNMAPPED, lambda u, a, ad, sz, v, d: self.unmapped.append(hex(ad)) or False)

    def on_tick(self, uc, addr, size, ud):
        self.ticks += 1
        for h in self.tick_hook: h()

    def on_in(self, uc, port, size, ud):
        if port == 0x61: return self.p61
        if port == 0x60: return self.p60
        if port == 0x40:
            self.pit = (self.pit + self.pit_step) & 255
            return self.pit
        return 0

    def on_out(self, uc, port, size, v, ud):
        if port == 0x61: self.p61 = v & 0xFF
        self.outs.append((port, size, v & (0xFFFF if size == 2 else 0xFF)))

    def on_intr(self, uc, n, ud):
        ax = uc.reg_read(UC_X86_REG_AX)
        self.ints.append((n, ax, uc.reg_read(UC_X86_REG_CX), uc.reg_read(UC_X86_REG_BX)))
        if n == 0x10: self.int10_dx.append(uc.reg_read(UC_X86_REG_DX))
        if n == 0x16 and self.keys:
            k = self.keys.pop(0); uc.reg_write(UC_X86_REG_AX, (0x1E << 8) | ord(k))     # BIOS returns scancode:ascii
        if n == 0x29: self.chars.append(ax & 0xFF)
        elif n == 0x20: self.exited = True; uc.emu_stop()
        if n == 0x21 and ax >> 8 == 9:                  # DOS print string: read DS:DX up to '$'
            base = (uc.reg_read(UC_X86_REG_DS) << 4) + uc.reg_read(UC_X86_REG_DX)
            buf = bytes(uc.mem_read(base, 64)); self.dos_strings.append(buf[:buf.index(b'$')])

    def run(self, instructions):
        done = 0
        while done < instructions and not self.exited:
            n = min(1_000_000, instructions - done)
            self.uc.emu_start(self.uc.reg_read(UC_X86_REG_IP) if done else 0x100, 0xFFFF0, count=n)
            done += n
        return self

def size_gate(name, r, limit):
    check(len(r.com) <= limit, f"{name}: {len(r.com)} bytes (under 9; budget {limit})")
    check(not r.unmapped, f"{name}: touches no memory outside video memory and its own segment {r.unmapped[:3]}")

def word(r, linear): return int.from_bytes(bytes(r.uc.mem_read(linear, 2)), "little")

# ---------------------------------------------------------------- STACKMAP
print("== STACKMAP ==")
r = Run("STACKMAP.COM").run(200_000)
size_gate("STACKMAP", r, 7)
check(r.uc.reg_read(UC_X86_REG_SS) == 0xB800, "the stack segment is the text screen (SS = B800h)")
cells = [word(r, 0xB8000 + a) for a in range(0, 4000, 2)]
check(all(c == a + 2 for c, a in zip(cells, range(0, 4000, 2))), "every screen cell holds its own address (+2): character = low byte, colour = high byte")
check(len({c & 255 for c in cells[:80]}) == 80 and len({c >> 8 for c in cells}) >= 15, "so the screen is a map: 80 different characters per row, and colours that step down it")

# ---------------------------------------------------------------- STKRAIN
print("\n== STKRAIN ==")
r = Run("STKRAIN.COM").run(400_000)
size_gate("STKRAIN", r, 8)
vals = [word(r, 0xB8000 + a) for a in range(0, 4000, 2)]
steps = {(a - b) & 0xFFFF for a, b in zip(vals, vals[1:])}
check(r.uc.reg_read(UC_X86_REG_SS) == 0xB800 and steps == {1}, f"consecutive screen cells hold consecutive counter values (steps {sorted(steps)})")
check(len({v & 255 for v in vals}) == 256 and len({v >> 8 for v in vals}) >= 7, "the characters run through all 256 codes and the colours step through 8 values down the screen")

# ---------------------------------------------------------------- BULLETS
print("\n== BULLETS ==")
r = Run("BULLETS.COM").run(200_000)
size_gate("BULLETS", r, 7)
cells = {word(r, 0xB8000 + a) for a in range(0, 4000, 2)}
check(r.uc.reg_read(UC_X86_REG_SS) == 0xB800 and cells == {0x0107}, f"the whole screen is the CALL's return address, 0107h: character 07h (a bullet), colour 01h (blue) {sorted(map(hex, cells))}")
check(len(r.outs) == 0 and not r.unmapped, "it recurses forever without calling anything")

# ---------------------------------------------------------------- SNOW
print("\n== SNOW ==")
r = Run("SNOW.COM").run(5000)
size_gate("SNOW", r, 8)
want = [((13 * (i + 1)) & 255) | 0x80 for i in range(len(r.chars))]
check(len(r.chars) > 800 and r.chars == want, f"prints the timer counter (port 40h) with bit 7 forced on, over and over ({len(r.chars)} characters)")
check(min(r.chars) >= 128 and len(set(r.chars)) > 30, "so only codes 128-255 appear (no control codes to disturb the screen), and plenty of different ones")

# ---------------------------------------------------------------- BREATH
print("\n== BREATH ==")
r = Run("BREATH.COM", hlt_as_tick=True).run(6000)
size_gate("BREATH", r, 7)
shapes = [cx for n, ax, cx, bx in r.ints if n == 0x10 and ax >> 8 == 1]
check(r.com[0] == 0x96, "starts with XCHG AX,SI: DOS gives SI = 0100h, which makes AH = 1 (set cursor shape)")
check(len(shapes) > 200 and all(b - a == 1 for a, b in zip(shapes, shapes[1:])), f"BIOS set-cursor-shape (AH = 1) once per tick, the shape counting up by one ({len(shapes)} calls)")
check(r.ticks >= len(shapes) - 1, f"after each call it waits a timer tick (HLT x{r.ticks})")

# ---------------------------------------------------------------- BUZZ
print("\n== BUZZ ==")
r = Run("BUZZ.COM").run(4000)
size_gate("BUZZ", r, 6)
vals = [v for p, s, v in r.outs if p == 0x61]
check(len(vals) > 500 and vals[:4] == [2, 0, 2, 0] and set(vals) == {0, 2}, "port 61h gets 2, 0, 2, 0, ...: bit 1 (the speaker cone) toggles on every write")

# ---------------------------------------------------------------- STATIC
print("\n== STATIC ==")
r = Run("STATIC.COM").run(4000)
size_gate("STATIC", r, 6)
outs = [v for p, s, v in r.outs if p == 0x61]
want = [(13 * (i + 1)) & 255 for i in range(len(outs))]
check(len(outs) > 500 and outs == want, "port 61h is written with the timer counter (port 40h) it just read")
check(len({v & 3 for v in outs}) == 4, "so the speaker gate/cone bits take all four combinations: noise")

# ---------------------------------------------------------------- TICKER
print("\n== TICKER ==")
r = Run("TICKER.COM", hlt_as_tick=True).run(4000)
size_gate("TICKER", r, 6)
outs = [v for p, s, v in r.outs if p == 0x61]
check(len(outs) > 200 and all((b - a) & 255 == 1 for a, b in zip(outs, outs[1:])) and outs[:4] == [1, 2, 3, 4], f"the speaker bits step 1,2,3,0,1.. once per tick (first writes {outs[:5]})")
check(r.ticks >= len(outs) - 1, f"with a HLT (one 55 ms tick) between writes (x{r.ticks})")

# ---------------------------------------------------------------- GEIGER
print("\n== GEIGER ==")
r = Run("GEIGER.COM", hlt_as_tick=True).run(4000)
size_gate("GEIGER", r, 7)
outs = [v for p, s, v in r.outs if p == 0x61]
want = [(13 * (i + 1)) & 255 for i in range(len(outs))]
check(len(outs) > 200 and outs == want and len({v & 3 for v in outs}) == 4, "port 61h gets the timer counter, a random value, one per tick")
check(r.ticks >= len(outs) - 1, f"held for a whole tick each time (HLT x{r.ticks})")

# ---------------------------------------------------------------- TYPER
print("\n== TYPER ==")
r = Run("TYPER.COM"); r.keys = list("hello, world")
r.run(3000)
size_gate("TYPER", r, 7)
calls = [ax for n, ax, cx, bx in r.ints if n == 0x16]
check(len(calls) > 12 and all(ax >> 8 == 0 for ax in calls), "waits for a key with BIOS INT 16h, AH = 0 on every call (CBW clears the scan code)")
check(r.chars[:12] == [ord(c) for c in "hello, world"], "and prints each key it gets, in order")

# ---------------------------------------------------------------- MIRROR
print("\n== MIRROR ==")
r = Run("MIRROR.COM").run(2000)
size_gate("MIRROR", r, 8)
check(r.dos_strings == [r.com[:-1]], f"DOS print-string is called once, with the program's own bytes up to the '$': {r.dos_strings[0].hex() if r.dos_strings else None}")
check(r.com[-1:] == b"$" and r.exited, "the eighth byte is the '$' terminator, and RET returns to the PSP's INT 20h: it exits cleanly")

# ---------------------------------------------------------------- SPECTRUM
print("\n== SPECTRUM ==")
r = Run("SPECTRUM.COM").run(400_000)
size_gate("SPECTRUM", r, 8)
mem = bytes(r.uc.mem_read(0xB8000, 4000))
ok_attr = all(mem[2 * c + 1] == (2 * c + 3) & 255 for c in range(1999))
ok_char = all(mem[2 * c + 2] == (2 * c + 3) >> 8 for c in range(1999))
check(r.uc.reg_read(UC_X86_REG_SS) == 0xB800 and (r.uc.reg_read(UC_X86_REG_SP) & 1) == 1, "the stack is the text screen and SP is odd, so every pushed word straddles two cells")
check(ok_attr and ok_char, "each cell's colour byte is the low byte of its address and each glyph byte the high byte: a colour that changes every cell, a glyph that changes every 128")
check(len({mem[i] for i in range(1, 4000, 2)}) >= 100, "so the screen is a wall of different colour attributes")

# ---------------------------------------------------------------- STRIPE
print("\n== STRIPE ==")
r = Run("STRIPE.COM", hlt_as_tick=True).run(4000)
size_gate("STRIPE", r, 8)
writes = [(ax, cx, bx) for n, ax, cx, bx in r.ints if n == 0x10]
check(len(writes) > 200 and all(ax >> 8 == 9 and ax & 255 == 0 and cx == 0xFF for ax, cx, bx in writes), f"BIOS write-character-and-attribute (AH = 9) of a blank, 255 cells, every time ({len(writes)} calls)")
check(all(b - a == 1 for a, b in zip([w[2] for w in writes], [w[2] for w in writes][1:])) and r.ticks >= len(writes) - 1, "the attribute (BL) counts up by one per call, with a timer tick between calls: a new colour every 55 ms")

# ---------------------------------------------------------------- BIG
print("\n== BIG ==")
r = Run("BIG.COM").run(500)
size_gate("BIG", r, 4)
check(r.com == b"\x40\xCD\x10\xC3", "inc ax / int 10h / ret")
check([ax for n, ax, cx, bx in r.ints if n == 0x10] == [1] and r.exited, "one INT 10h with AX = 1 (video mode 1: 40x25 text), then it exits cleanly")

# ---------------------------------------------------------------- TALL
print("\n== TALL ==")
r = Run("TALL.COM").run(500)
size_gate("TALL", r, 6)
calls = [(ax, bx) for n, ax, cx, bx in r.ints if n == 0x10]
check(calls == [(0x1112, 0)] and r.exited, "one INT 10h with AX = 1112h (load the ROM 8x8 font, recompute the screen: 80x50) and BX = 0, then it exits cleanly")

# ---------------------------------------------------------------- KEYSCAN
print("\n== KEYSCAN ==")
r = Run("KEYSCAN.COM"); r.p60 = 0x1E
r.run(3000)
n1 = len(r.chars); r.p60 = 0x9E; r.run(3000)
size_gate("KEYSCAN", r, 6)
check(n1 > 500 and set(r.chars[:n1]) == {0x1E} and set(r.chars[n1 + 5:]) == {0x9E}, "prints whatever the keyboard port (60h) holds, over and over: the make code 1Eh, then the break code 9Eh after the key is released")

# ---------------------------------------------------------------- PSPBACK
print("\n== PSPBACK ==")
r = Run("PSPBACK.COM")
tail = b" hello tiny world\r"
r.uc.mem_write(LIN + 0x80, bytes([len(tail)]) + tail)           # the command tail DOS would have put in the PSP
r.run(5000)
size_gate("PSPBACK", r, 7)
psp = bytes(r.uc.mem_read(LIN, 0x101))
check(r.chars == [psp[0x100 - i] for i in range(255)] and r.exited, "prints the 255 bytes at 0100h, 00FFh, 00FEh, ... downwards (the PSP backwards) and then exits cleanly")
text = bytes(r.chars)
check(b"dlrow ynit olleh" in text, "so the command line comes out reversed: 'dlrow ynit olleh'")

# ---------------------------------------------------------------- STATE
print("\n== STATE ==")
r = Run("STATE.COM").run(400_000)
size_gate("STATE", r, 7)
w = [word(r, 0xB8000 + 2 * c) for c in range(2000)]
want = {0: 0x0100, 1: 0x091C, 3: 0x0000, 4: SEG, 5: 0x00FF, 6: 0x0000, 7: 0xFFFE}     # SI BP (SP) BX DX CX AX DI: PUSHA's order, ascending, one cell off the tile edge
ok = all(w[c] == want[c % 8] for c in range(2000) if c % 8 in want)
check(r.uc.reg_read(UC_X86_REG_SS) == 0xB800 and ok, "the screen is an 8-cell tile repeated: SI, BP, (SP), BX, DX, CX, AX, DI exactly as the machine started the program")
check(len({w[c] for c in range(2, 2000, 8)}) > 100, "and the SP cell of each tile counts down by 16: a glyph column that drifts")

# ---------------------------------------------------------------- FLUX
print("\n== FLUX ==")
r = Run("FLUX.COM").run(500_000)
size_gate("FLUX", r, 8)
w = [word(r, 0xB8000 + 2 * c) for c in range(2000)]
want = {0: 0x0100, 1: 0x091C, 3: 0x0000, 4: SEG, 6: 0x0000, 7: 0xFFFE}
check(r.uc.reg_read(UC_X86_REG_SS) == 0xB800 and all(w[c] == want[c % 8] for c in range(2000) if c % 8 in want), "an 8-cell register tile as in STATE: SI, BP, BX, DX, AX, DI as DOS left them")
steps = {(b - a) & 0xFFFF for a, b in zip(w[5::8], w[13::8])}
check(steps == {1} and len({w[c] for c in range(5, 2000, 8)}) > 100, f"but CX, which is one lower for each tile pushed, makes a second drifting column (tile-to-tile steps {sorted(steps)})")

# ---------------------------------------------------------------- WEAVE
print("\n== WEAVE ==")
r = Run("WEAVE.COM").run(500_000)
size_gate("WEAVE", r, 8)
w = [word(r, 0xB8000 + 2 * c) for c in range(2000)]
blue = [c for c in range(2000) if w[c] == 0x0100]
addr = [c for c in range(2000) if w[c] != 0x0100]
check(r.uc.reg_read(UC_X86_REG_SS) == 0xB800 and len(blue) == 1000 and all(c % 2 == blue[0] % 2 for c in blue), "every other cell is SI's start-up value 0100h (a blank cell, blue attribute)")
check(all(w[c] == 2 * c + 2 for c in addr), "and the cells between hold their own address, as in STACKMAP")

# ---------------------------------------------------------------- CODEPAL
print("\n== CODEPAL ==")
r = Run("CODEPAL.COM").run(500)
size_gate("CODEPAL", r, 8)
calls = [(ax, cx, bx) for n, ax, cx, bx in r.ints if n == 0x10]
check(calls == [(0x1012, 0xFF, 0)] and r.int10_dx == [0x100] and r.exited, "one INT 10h, AX = 1012h (load DAC registers), BX = 0, CX = 255, ES:DX = 0100h: the program's own bytes; then it exits")
check(r.com[:3] == b"\xB8\x12\x10" and r.com[3:5] == b"\x89\xF2", "so DAC colour 0 is B8 12 10 (red 38h, green 12h, blue 10h in 6 bits) and colour 1 is 89 F2 CD")

# ---------------------------------------------------------------- PSPPAL
print("\n== PSPPAL ==")
r = Run("PSPPAL.COM").run(500)
size_gate("PSPPAL", r, 7)
calls = [(ax, cx, bx) for n, ax, cx, bx in r.ints if n == 0x10]
check(calls == [(0x1012, 0xFF, 0)] and r.int10_dx == [0] and r.exited, "one INT 10h, AX = 1012h, BX = 0, CX = 255, ES:DX = 0: the start of the PSP (CWD makes DX = 0); then it exits")

# ---------------------------------------------------------------- NOISEPAL
print("\n== NOISEPAL ==")
r = Run("NOISEPAL.COM").run(4000)
size_gate("NOISEPAL", r, 8)
outs = [(p, v) for p, sz, v in r.outs]
check(len(outs) > 500 and all(p == 0x3C9 for p, v in outs), "every write goes to the VGA DAC data port 3C9h")
check([v for p, v in outs] == [(13 * (i + 1)) & 255 for i in range(len(outs))], "each value is the timer counter (port 40h) just read: random colour components for red, green, blue, red, ...")
check(bytes(r.uc.mem_read(0xB8000, 4000)) == bytes(4000), "and no screen memory is touched: the picture is whatever was already there")

# ---------------------------------------------------------------- MODE3
print("\n== MODE3 ==")
r = Run("MODE3.COM").run(500)
size_gate("MODE3", r, 5)
check([ax for n, ax, cx, bx in r.ints if n == 0x10] == [3] and r.exited, "one INT 10h with AX = 3 (set video mode 3: 80x25 text, default palette), then it exits")

# ---------------------------------------------------------------- EVO1 / EVO2
for name, seg, op in (("EVO1", 0xB0FD, 0xA7), ("EVO2", 0xB0DD, 0xA6)):
    print(f"\n== {name} ==")
    r = Run(f"{name}.COM").run(600_000)
    size_gate(name, r, 8)
    check(r.com == bytes([0x68, seg & 255, seg >> 8, 0x17, 0x60, op, 0xEB, 0xFC]), f"push {seg:04X}h / pop ss / pusha / {'cmpsw' if op == 0xA7 else 'cmpsb'} / jmp")
    w = [word(r, 0xB8000 + 2 * c) for c in range(2000)]
    bp = [c for c in range(2000) if w[c] == 0x091C]
    check(r.uc.reg_read(UC_X86_REG_SS) == seg and len(bp) > 150 and max(sum(1 for c in bp if c % 8 == k) for k in range(8)) >= 0.95 * len(bp), "the stack segment is off the text page, yet the register tile still shows up on it: BP's start-up value 091Ch sits in one column of every tile (the drifting DI or SI column meets 091Ch only by chance)")
    check(len(set(w)) > 400, f"and the screen is rich: {len(set(w))} distinct cells, with the SI and DI columns drifting")

# ---------------------------------------------------------------- OVERLAP / OVERSUB
import random
for name, mid, mnem in (("OVERLAP", 0x30, "xor"), ("OVERSUB", 0x28, "sub")):
    print(f"\n== {name} ==")
    want = bytes([0xC5, mid, 0x04, 0xAD, 0xE6, 0x61, 0xEB, 0xF9])
    r = Run(f"{name}.COM"); size_gate(name, r, 8)
    check(r.com == want, f"bytes C5 {mid:02X} 04 AD E6 61 EB F9: the JMP lands one byte into the first instruction, so the same bytes decode as {mnem} [si],al / lodsw / out 61h,al / jmp")
    r.run(100_000)
    ds = r.uc.reg_read(UC_X86_REG_DS)
    check(ds == 0xAD04, f"pass 1 loads DS from the program's own bytes (SI = 0100h at entry, not the PSP): DS = {ds:04X}h")
    vals = [v for p, s_, v in r.outs if p == 0x61]
    check(len(vals) > 5000 and vals[0] == 0xAD and not r.unmapped, f"first speaker write is ADh, then it loops without any delay ({len(vals)} writes)")
    toggles = sum(1 for a, b in zip(vals, vals[1:]) if (a ^ b) & 2)
    if name == "OVERSUB":
        check(vals[:4] == [0xAD, 0x53, 0xAD, 0x53] and toggles == len(vals) - 1, "SUB negates AL every step, so the speaker cone toggles on every write even over empty memory")
    else:
        check(toggles == 0, "over empty memory XOR leaves AL at ADh: no tone at all (it only sounds when the memory it walks holds data)")
    # now with data in the window DS:SI walks (AD040h-BD03Fh, which includes the B800h text page)
    r2 = Run(f"{name}.COM"); rnd = random.Random(1)
    r2.uc.mem_write(0xAD040, bytes(rnd.randrange(256) for _ in range(0x10000)))
    before = bytes(r2.uc.mem_read(0xB8000, 4000)); r2.run(300_000)
    vals = [v for p, s_, v in r2.outs if p == 0x61]
    toggles = sum(1 for a, b in zip(vals, vals[1:]) if (a ^ b) & 2)
    check(len(set(vals)) > 200 and toggles > len(vals) * 0.3, f"with data in memory the output is noise: {len(set(vals))} distinct values, {toggles} cone toggles in {len(vals)} writes")
    after = bytes(r2.uc.mem_read(0xB8000, 4000))
    check(sum(1 for a, b in zip(before, after) if a != b) > 200, "and the walk crosses the B800h text page, so it also corrupts the screen: a noise-and-glitch demo")

# ---------------------------------------------------------------- OVERHEAR
print("\n== OVERHEAR ==")
r = Run("OVERHEAR.COM"); size_gate("OVERHEAR", r, 8)
check(r.com == bytes([0xC5, 0x38, 0x04, 0xAD, 0xE6, 0x61, 0xEB, 0xF9]), "bytes C5 38 04 AD E6 61 EB F9: the OVERLAP trick with 38h, so the loop is cmp [si],al / lodsw / out 61h,al / jmp")
r.uc.mem_write(0xAD040, bytes(i & 255 for i in range(0x10000)))
before = bytes(r.uc.mem_read(0xAD040, 0x10000)); r.run(60_000)
vals = [v for p, s_, v in r.outs if p == 0x61]
check(vals[0] == 0xAD and vals[1:200] == [(0x100 + 2 * k) & 255 for k in range(199)], "after the first ADh it sends the low byte of each successive word of the window to the speaker port: it reads the memory out loud")
check(bytes(r.uc.mem_read(0xAD040, 0x10000)) == before and r.uc.reg_read(UC_X86_REG_DS) == 0xAD04, "and it never writes: the memory it walks (which includes the B800h text page) is untouched")

print("\nRESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILED:\n  - " + "\n  - ".join(fails))
sys.exit(1 if fails else 0)
