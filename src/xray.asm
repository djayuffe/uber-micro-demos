; XRAY - 7 bytes. Prints the computer's low memory as text.
BITS 16
ORG 100h
    mov ds,ax         ; 8E D8     AX = 0 at entry: DS = segment 0 (the interrupt vectors)
.l: lodsb             ; AC        next byte of RAM, starting at 0000:0100
    int 29h           ; CD 29     ...printed as a character
    jmp short .l      ; EB FB
