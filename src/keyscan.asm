; KEYSCAN - 6 bytes. Floods the screen with the glyph of the last keyboard scancode.
BITS 16
ORG 100h
.l: in al,60h         ; E4 60     the keyboard controller's last byte: make code on press, +80h on release
    int 29h           ; CD 29     print it, over and over
    jmp short .l      ; EB FA
