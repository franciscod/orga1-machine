# orga1-machine
acercando la máquina de orga 1 a los bits

- simulador
- ensamblador
- desensamblador

http://www.dc.uba.ar/materias/oc1/2015/c1

## anda?

### ensambla
	$ python asm.py etc/p2.asm
	19c80004b00000050fe039a7c000
	$ cat etc/p2.hex
	19C80004B00000050FE039A7C000

### desensambla
	$ python disasm.py etc/p1.hex
	MOV R1, [[0006]]
	ADD [R1], 6000
	JMP 0000
	DW 0007
	DW 0004

### corre
	$ python -i sim.py etc/p2.hex
	ready
	>>> maq.run()
	executing MOV R7, [0004]
	executing CALL 0005
	executing SUB R6, R7
	executing RET
	end of execution

### da pasitos (...sirve para debuggear?)
	python -i sim.py etc/do.hex

	>>> maq.step(); maq.R

### vuela etiquetas
	python disasm.py <(python asm.py etc/p1.asm)
