; OVERMAX - 8 bytes. OVERLAP turned up: one byte changes (ADh -> ACh), so the second program uses LODSB instead
; of LODSW and the walk steps one byte at a time. Every character AND every colour byte it crosses is XORed.
BITS 16
ORG 100h
    lds si,[bx+si]    ; C5 30   pass 1: DS:SI = the dword at DS:0100h, this program's own bytes: SI = 30C5h, DS = AC04h
    add al,0ACh       ; 04 AC   (AL = ACh)
    out 61h,al        ; E6 61   speaker port
    jmp short $-5     ; EB F9   lands on the 30h: xor [si],al / lodsb / out 61h,al / jmp ...
                      ; the window AC040h + 30C5h .. walks AF105h-BF104h, which contains the B800h text page
