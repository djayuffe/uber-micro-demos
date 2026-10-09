; TYPER - 7 bytes. A typewriter: whatever you press is echoed back, forever.
BITS 16
ORG 100h
.l: int 16h           ; CD 16     BIOS keyboard, AH = 0: wait for a key, return it in AL
    int 29h           ; CD 29     print it
    cbw               ; 98        AH = 0 again for the next wait (ASCII keys are < 128)
    jmp short .l      ; EB F9
