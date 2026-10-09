; BUZZ - 6 bytes. Flip the PC speaker as fast as the CPU can.
BITS 16
ORG 100h
.l: xor al,2          ; 34 02     bit 1 of port 61h is the speaker cone (AL = 0 at entry)
    out 61h,al        ; E6 61
    jmp short .l      ; EB FA
