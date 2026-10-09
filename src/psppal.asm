; PSPPAL - 7 bytes. DOS's own Program Segment Prefix becomes the screen's palette, and stays so after the program exits.
BITS 16
ORG 100h
    mov ax,1012h      ; B8 12 10  BIOS: load DAC colour registers BX.. (BX = 0), CX of them (CX = 00FFh), from ES:DX
    cwd               ; 99        AX is positive, so DX = 0: ES:0 is the start of the PSP
    int 10h           ; CD 10     colour 0 = CD 20 FF (the INT 20h opcode and the top-of-memory segment), ...
    ret               ; C3
