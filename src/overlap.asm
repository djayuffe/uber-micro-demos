; OVERLAP - 8 bytes, two programs in the same bytes. The JMP lands one byte INTO the first instruction.
BITS 16
ORG 100h
    lds si,[bx+si]    ; C5 30   pass 1: DS:SI = the dword at DS:0100h = this program's own first bytes
    add al,0ADh       ; 04 AD   (SI = 30C5h, DS = AD04h: the VGA/text window; AL = ADh)
    out 61h,al        ; E6 61   speaker port
    jmp short $-5     ; EB F9   lands on the 30h: from now on the bytes read  xor [si],al / lodsw / out / jmp
