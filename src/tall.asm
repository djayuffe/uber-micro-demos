; TALL - 6 bytes. 80x50 text: the BIOS reloads the 8x8 font, which doubles the number of rows.
BITS 16
ORG 100h
    mov ax,1112h      ; B8 12 11  BIOS: load the ROM 8x8 font and recompute the screen (BL = 0: block 0, BX = 0 at entry)
    int 10h           ; CD 10
    ret               ; C3
