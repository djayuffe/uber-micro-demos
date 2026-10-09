; MIRROR - 8 bytes. A program that prints its own machine code, then exits cleanly.
BITS 16
ORG 100h
    mov ah,9          ; B4 09     DOS: print the '$'-terminated string at DS:DX
    mov dx,si         ; 89 F2     DOS gives SI = 0100h, where this very program starts
    int 21h           ; CD 21
    ret               ; C3        the word at the top of the stack is 0: back to the PSP's INT 20h
    db '$'            ; 24        the terminator is the eighth byte of the file
