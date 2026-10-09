; STKRAIN - 8 bytes. The stack is the screen, and a counter pours down it.
BITS 16
ORG 100h
    push 0B800h       ; 68 00 B8
    pop ss            ; 17
.l: inc ax            ; 40
    push ax           ; 50        low byte = character, high byte = colour
    jmp short .l      ; EB FC
