main:   MOV R1, [[et1]]
        ADD [R1], 0x6000
        JMP main
et1:    DW 0x0007
et2:    DW 0x0004
