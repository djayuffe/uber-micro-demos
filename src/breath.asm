; BREATH - 7 bytes. The text cursor pulses: its height changes on every timer tick.
BITS 16
ORG 100h
    xchg ax,si        ; 96        DOS gives SI = 0100h: AX = 0100h, i.e. AH = 1 (BIOS: set cursor shape)
.l: int 10h           ; CD 10     CH = start line, CL = end line
    inc cx            ; 41        a new shape...
    hlt               ; F4        ...every 55 ms
    jmp short .l      ; EB F9
