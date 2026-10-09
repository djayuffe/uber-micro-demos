; STRIPE - 8 bytes. A three-row colour band at the cursor, changing colour every timer tick.
BITS 16
ORG 100h
    mov ah,9          ; B4 09     BIOS: write character AL with attribute BL, CX times
.l: int 10h           ; CD 10     AL = 0 (blank), CX = 00FFh (255 cells), BH = page 0
    inc bx            ; 43        BL = the attribute: a new colour...
    hlt               ; F4        ...every 55 ms
    jmp short .l      ; EB F9
