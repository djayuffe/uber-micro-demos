; CODEPAL - 8 bytes. The program's own machine code becomes the screen's palette, and it stays that way after it exits.
BITS 16
ORG 100h
    mov ax,1012h      ; B8 12 10  BIOS: load DAC colour registers BX.. (BX = 0), CX of them (CX = 00FFh), from ES:DX
    mov dx,si         ; 89 F2     DOS gives SI = 0100h: the table is this program's own bytes
    int 10h           ; CD 10     (each colour is three bytes, 6 bits each: colour 0 = B8 12 10, colour 1 = 89 F2 CD, ...)
    ret               ; C3        and out, leaving the colours behind
