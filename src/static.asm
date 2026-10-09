; STATIC - 6 bytes. White noise: the timer's fastest-changing bits drive the speaker.
BITS 16
ORG 100h
.l: in al,40h         ; E4 40     PIT counter, low byte: ticks every 0.84 us
    out 61h,al        ; E6 61     its low two bits are the speaker gate and cone
    jmp short .l      ; EB FA
