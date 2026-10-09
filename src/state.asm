; STATE - 7 bytes. The machine's own start-up state, painted on the screen: PUSHA stacks the eight registers DOS leaves behind.
BITS 16
ORG 100h
    push 0B800h       ; 68 00 B8
    pop ss            ; 17        the stack is the text screen
.l: pusha             ; 60        AX CX DX BX SP BP SI DI, as DOS and this PC happened to leave them
    jmp short .l      ; EB FD
