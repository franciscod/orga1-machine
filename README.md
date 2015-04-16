# orga1-machine
acercando la máquina de orga 1 a los bits

- simulador
- ensamblador
- desensamblador

http://www.dc.uba.ar/materias/oc1/2015/c1

## anda?

### ensambla
	$ python om.py asm etc/p2.asm
	19c80004b00000050fe039a7c000
	$ cat etc/p2.hex
	19C80004B00000050FE039A7C000

### desensambla
	$ python om.py disasm etc/p1.hex
	MOV R1, [[0006]]
	ADD [R1], 6000
	JMP 0000
	DW 0007
	DW 0004

### corre
	$ python om.py run etc/p2.hex

	executing MOV R7, [0004]
	executing CALL 0005
	executing SUB R6, R7
	executing RET
	end of execution

### da pasitos (...sirve para debuggear?)
	python om.py load etc/do.hex

	>>> m.step(); m.R

### vuela etiquetas
	python om.py disasm <(python om.py asm etc/p1.asm)
