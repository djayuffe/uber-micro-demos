; SPECTRUM - 8 bytes. STACKMAP with the stack one byte off: attribute and character swap speeds.
BITS 16
ORG 100h
    push 0B800h       ; 68 00 B8
    pop ss            ; 17        the stack is the text screen
    dec sp            ; 4C        SP is odd: every word lands across two cells
.l: push sp           ; 54        low byte -> a colour that changes every cell,
    jmp short .l      ; EB FD     high byte -> a glyph that changes every 128
