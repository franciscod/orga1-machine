# orga1-machine
acercando la máquina de orga 1 a los bits

http://www.dc.uba.ar/materias/oc1/2015/c1

## anda?
	python -i sim.py etc/p1.hex

	# corre y corre
	>>> maq.run()

	python -i sim.py etc/do.hex

	# debugger primitivo
	>>> maq.step(); maq.R
---

```
things you probably haven't realised you need yet: an ABI/calling convention; an exception model
"what happens when you dereference a NULL pointer?"
"what happens when you execute the instruction for a system call?"
"what happens if you try to execute something that's not a valid instruction?"
```
