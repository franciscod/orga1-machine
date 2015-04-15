# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
from machine import Orga1Machine
from insns import InvalidInstruction

if __name__ == '__main__':
    maq = Orga1Machine()

    with open(sys.argv[1]) as f:
        i = 0
        while True:
            h = f.read(4)
            if h == '\n':
                break

            maq.M.set(i, int(h, 16))
            i += 1


    while maq.PC.get() < i:
        try:
            print ("%04x: " % maq.PC.get(), end='')
            w = maq._fetch()
            insn = maq._decode(w)
            print (insn)

        except InvalidInstruction:
            print ("DW %04x" % w.get())
