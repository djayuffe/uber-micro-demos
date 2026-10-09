; BREATH - 8 bytes. The text cursor pulses: its height changes on every timer tick.
BITS 16
ORG 100h
    mov ah,1          ; B4 01     BIOS: set cursor shape (CH = start line, CL = end line)
.l: int 10h           ; CD 10
    inc cx            ; 41        a new shape...
    hlt               ; F4        ...every 55 ms
    jmp short .l      ; EB F9
