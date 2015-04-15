# -*- coding: utf-8 -*-

import sys
from machine import Orga1Machine

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

    print ("ready")
