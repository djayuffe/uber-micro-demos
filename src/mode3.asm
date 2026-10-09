; MODE3 - 5 bytes. Back to 80x25 text with the default palette: undoes BIG, TALL, CODEPAL and PSPPAL.
BITS 16
ORG 100h
    mov al,3          ; B0 03     AX = 0 at entry: AX = 0003h, "set video mode 3" (which reloads the default palette)
    int 10h           ; CD 10
    ret               ; C3
