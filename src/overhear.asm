; OVERHEAR - 8 bytes. The OVERLAP trick with CMP (38h): the loop only READS memory, so nothing is scribbled on.
BITS 16
ORG 100h
    lds di,[bx+si]    ; C5 38   pass 1: DS = AD04h (from the program's own bytes); DI is loaded, SI stays 0100h
    add al,0ADh       ; 04 AD
    out 61h,al        ; E6 61
    jmp short $-5     ; EB F9   lands on the 38h: cmp [si],al / lodsw / out 61h,al / jmp ...
                      ; ... and every word of the AD040h-BD03Fh window, text page included, goes to the speaker port
