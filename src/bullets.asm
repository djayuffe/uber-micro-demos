; BULLETS - 7 bytes. Infinite recursion, with the stack pointed at the screen.
BITS 16
ORG 100h
    push 0B800h       ; 68 00 B8
    pop ss            ; 17
.l: call .l           ; E8 FD FF  every call pushes its return address: a screen of blue bullets
