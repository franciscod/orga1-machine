# -*- coding: utf-8 -*-

# TODO: figure out why tallerC1p3.asm doesn't end at DEAD

import sys
from insns import InvalidInstruction
from machine import Orga1Machine
from asm import parse

def load_hex(machine, path):
    with open(path) as f:
        i = 0
        while True:
            h = f.read(4)
            if h == '\n':
                break

            machine.M.set(i, int(h, 16))
            i += 1
    return i

def usage():
    print (
"""usage:
{} [-i] {} MODE [FILE]

available modes (some of them are more useful with -i):
  blank:   gives you a blank machine
  load:    loads a .hex file
  run:     loads and runs a .hex file
  asm:     assembles a .asm file
  disasm:  disassembles a .hex file
""".format(sys.executable, sys.argv[0]))


if __name__ == '__main__':
    m = Orga1Machine()
    wc = 0

    if len(sys.argv) < 2:
        usage()
        exit(1)


    if len(sys.argv) < 3:
        print ("FILE argument is missing")
        exit(2)

    if sys.argv[1] in ('run', 'load', 'disasm'):
        wc = load_hex(m, sys.argv[2])

    if sys.argv[1] == 'run':
        m.run()
        exit(0)

    if sys.argv[1] == 'asm':
        tokens = parse(open(sys.argv[2]).readlines())
        for token in tokens:
            print ('%04x' % token.asm(), end='')
        print ('')
        exit(0)

    if sys.argv[1] == 'disasm':
        while m.PC.get() < wc:
            try:
                # TODO: make this optional
                # print ("%04x: " % m.PC.get(), end='')
                w = m._fetch()
                insn = m._decode(w)
                print (insn)

            except InvalidInstruction:
                print ("DW %04x" % w.get())
        exit(0)

    print ("ready, hope you've used '-i'")
