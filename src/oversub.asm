; OVERSUB - 8 bytes. OVERLAP with SUB for XOR (the 30h becomes 28h, so LDS loads BP and leaves SI alone).
BITS 16
ORG 100h
    lds bp,[bx+si]    ; C5 28   pass 1: DS = the word at DS:0102h (AD04h: the VGA/text window); SI stays 0100h
    add al,0ADh       ; 04 AD   AL = ADh
    out 61h,al        ; E6 61   speaker port
    jmp short $-5     ; EB F9   lands on the 28h: sub [si],al / lodsw / out / jmp (AL flips ADh, 53h, ADh ...: always a tone)
