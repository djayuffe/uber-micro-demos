; SNOW - 8 bytes. A blizzard of random glyphs: the timer's fast counter, forced into 128..255.
BITS 16
ORG 100h
.l: in al,40h         ; E4 40     PIT counter, low byte: changes every 0.84 us
    or al,80h         ; 0C 80     codes 128-255 only: accents, box drawing, maths, no control codes
    int 29h           ; CD 29     print it
    jmp short .l      ; EB FA
