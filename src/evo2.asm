; EVO2 - 8 bytes. Found by evolution, not written: EVO1's cousin, a different segment and CMPSB instead of CMPSW.
BITS 16
ORG 100h
    push 0B0DDh       ; 68 DD B0
    pop ss            ; 17
.l: pusha             ; 60
    cmpsb             ; A6        SI and DI advance by 1 each time round, not 2
    jmp short .l      ; EB FC
