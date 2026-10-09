; TYPER - 8 bytes. A typewriter: whatever you press is echoed back, forever.
BITS 16
ORG 100h
.l: xor ah,ah         ; 30 E4     BIOS keyboard: AH = 0 waits for a key and returns it in AL
    int 16h           ; CD 16
    int 29h           ; CD 29     print it
    jmp short .l      ; EB F8
