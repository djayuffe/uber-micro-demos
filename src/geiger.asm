; GEIGER - 7 bytes. A Geiger counter: random clicks, 18 a second.
BITS 16
ORG 100h
.l: in al,40h         ; E4 40     the timer's fast-changing counter is the random source
    out 61h,al        ; E6 61     its low two bits set the speaker gate and cone
    hlt               ; F4        ...and hold that for one 55 ms tick
    jmp short .l      ; EB F9
