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
        self.outs, self.ints, self.chars, self.unmapped, self.ticks = [], [], [], [], 0
        self.p61, self.pit, self.pit_step = port61, 0, pit_step
        self.tick_hook = []
        self.keys = []
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
        if n == 0x16 and self.keys:
            k = self.keys.pop(0); uc.reg_write(UC_X86_REG_AX, (0x1E << 8) | ord(k))     # BIOS returns scancode:ascii
        if n == 0x29: self.chars.append(ax & 0xFF)
        elif n == 0x20: uc.emu_stop()

    def run(self, instructions):
        done = 0
        while done < instructions:
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

# ---------------------------------------------------------------- STACKRAIN
print("\n== STACKRAIN ==")
r = Run("STACKRAIN.COM").run(400_000)
size_gate("STACKRAIN", r, 8)
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

# ---------------------------------------------------------------- XRAY
print("\n== XRAY ==")
r = Run("XRAY.COM").run(5000)
size_gate("XRAY", r, 7)
check(r.chars[:300] == [i & 255 for i in range(0x100, 0x100 + 300)], "prints the bytes of segment 0 (AX = 0 at entry gives DS = 0) in order from offset 0100h")
check(len(r.chars) > 800, f"and keeps going ({len(r.chars)} characters)")

# ---------------------------------------------------------------- BREATH
print("\n== BREATH ==")
r = Run("BREATH.COM", hlt_as_tick=True).run(6000)
size_gate("BREATH", r, 8)
shapes = [cx for n, ax, cx, bx in r.ints if n == 0x10 and ax >> 8 == 1]
check(len(shapes) > 200 and all(b - a == 1 for a, b in zip(shapes, shapes[1:])), f"BIOS set-cursor-shape (AH = 1) once per tick, the shape counting up by one ({len(shapes)} calls)")
check(r.ticks >= len(shapes) - 1, f"after each call it waits a timer tick (HLT x{r.ticks})")

# ---------------------------------------------------------------- BUZZ
print("\n== BUZZ ==")
r = Run("BUZZ.COM", port61=0x30).run(4000)
size_gate("BUZZ", r, 8)
vals = [v for p, s, v in r.outs if p == 0x61]
check(len(vals) > 500 and all(a ^ b == 2 for a, b in zip(vals, vals[1:])), "every write to port 61h flips bit 1 (the speaker cone) and keeps the other bits")

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
size_gate("TYPER", r, 8)
calls = [ax for n, ax, cx, bx in r.ints if n == 0x16]
check(len(calls) > 12 and all(ax >> 8 == 0 for ax in calls[:1]), "waits for a key with BIOS INT 16h, AH = 0")
check(r.chars[:12] == [ord(c) for c in "hello, world"], "and prints each key it gets, in order")

print("\nRESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILED:\n  - " + "\n  - ".join(fails))
sys.exit(1 if fails else 0)
