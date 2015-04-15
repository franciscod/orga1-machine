main:	MOV R7, [0x0004]
		CALL subs
		DW 0x0FE0
subs:	SUB R6, R7
		RET
