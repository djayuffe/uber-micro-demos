; NOISEPAL - 8 bytes. No pixel is touched: the palette registers are fed the timer's counter, so the screen's colours churn.
BITS 16
ORG 100h
    mov dx,3C9h       ; BA C9 03  VGA DAC data port (the write index is 0 after a mode set)
.l: in al,40h         ; E4 40     a fast-changing counter...
    out dx,al         ; EE        ...streamed in as red, green, blue, red, green, ... for all 256 colours, over and over
    jmp short .l      ; EB FB
