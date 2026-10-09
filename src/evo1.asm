; EVO1 - 8 bytes. Found by evolution, not written: a stack that starts half a screen off, with SI and DI drifting.
BITS 16
ORG 100h
    push 0B0FDh       ; 68 FD B0  a stack segment that is NOT the text page, but overlaps it, out of phase
    pop ss            ; 17
.l: pusha             ; 60        the start-up registers, as in STATE, painted wherever the stack lands
    cmpsw             ; A7        compares two memory words, which has one useful side effect: SI and DI both advance by 2
    jmp short .l      ; EB FC     ...so their columns drift, and the tile no longer lines up with the 80-column screen
