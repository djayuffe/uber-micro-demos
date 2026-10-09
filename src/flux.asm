; FLUX - 8 bytes. STATE with a second moving column: the register file, painted, while CX counts down.
BITS 16
ORG 100h
    push 0B800h       ; 68 00 B8
    pop ss            ; 17        the stack is the text screen
.l: pusha             ; 60        the eight start-up registers, as a repeating tile
    dec cx            ; 49        ...except CX, which is one lower every time, so its column drifts too
    jmp short .l      ; EB FC
