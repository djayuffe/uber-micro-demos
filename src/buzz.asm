; BUZZ - 8 bytes. Flip the PC speaker as fast as the CPU can.
BITS 16
ORG 100h
.l: in al,61h         ; E4 61
    xor al,2          ; 34 02     bit 1 = the speaker cone
    out 61h,al        ; E6 61
    jmp short .l      ; EB F8
