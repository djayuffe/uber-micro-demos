; PSPBACK - 7 bytes. Reads DOS's own Program Segment Prefix backwards: the command line, reversed, then the FCBs.
BITS 16
ORG 100h
    std               ; FD        walk memory downwards
.l: lodsb             ; AC        SI = 0100h at entry: the first byte read is the last byte of the PSP
    int 29h           ; CD 29     print it
    loop .l           ; E2 FB     CX = 00FFh at entry: all 255 bytes of the PSP below the program
    ret               ; C3        then back to DOS (the word on top of the stack is 0: the PSP's INT 20h)
