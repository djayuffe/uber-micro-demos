; STACKMAP - 7 bytes. The stack IS the screen, and every cell shows its own address.
BITS 16
ORG 100h
    push 0B800h       ; 68 00 B8
    pop ss            ; 17        the stack now lives in text-mode video memory
.l: push sp           ; 54        write SP onto the screen, 2 bytes lower each time
    jmp short .l      ; EB FD
