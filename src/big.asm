; BIG - 4 bytes. DOS starts a .COM with AX = 0 and 80x25 text on screen; AX = 1 is "set video mode 1".
BITS 16
ORG 100h
    inc ax            ; 40        mode 1: 40x25 text with big glyphs
    int 10h           ; CD 10
    ret               ; C3        the word at the top of the stack is 0: back to the PSP's INT 20h
