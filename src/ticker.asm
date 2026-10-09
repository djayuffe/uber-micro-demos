; TICKER - 6 bytes. A metronome: the speaker bits step through 0,1,2,3 on every timer tick.
BITS 16
ORG 100h
.l: inc ax            ; 40
    out 61h,al        ; E6 61     gate/cone pattern: click, tone, click-off...
    hlt               ; F4        18.2 ticks a second
    jmp short .l      ; EB F9
