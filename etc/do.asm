	MOV R0, 0x0002
	MOV R1, 0x0001
	MOV R2, 0x0001
do: MOV R3, R2
	ADD R3, R1
	MOV R1, R2
	MOV R2, R3
	SUB R0, 0x0001
	JG do
