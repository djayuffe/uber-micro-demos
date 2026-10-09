; WEAVE - 8 bytes. The stack is the screen: the address map woven with the SI register's start-up value.
BITS 16
ORG 100h
    push 0B800h       ; 68 00 B8
    pop ss            ; 17
.l: push sp           ; 54        the cell's own address
    push si           ; 56        DOS's SI = 0100h: a blank cell with a blue attribute
    jmp short .l      ; EB FC
