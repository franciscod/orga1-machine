# -*- coding: utf-8 -*-

# TODO: I/O

class Word(object):
    def __init__(self, val, sz):
        self._sz = sz
        self._sz_h = sz / 4
        self.set(val)

    def set(self, val):
        self._value = int(val) % (2 ** self._sz)

    def get(self):
        return self._value

    def get_bits(self, count=None, skip=0):
        if count is None:
            count = self._sz

        end = max(min(self._sz - skip - count, 2 ** self._sz - 1), 0)

        return (self._value >> end) & (2 ** count - 1)

    def is_signed(self):
        return bool(self._value & (2 ** (self._sz - 1)))

    def __int__(self):
        return self._value

    def __str__(self):
        return ("%%0%dx" % self._sz_h) % self._value

    def __repr__(self):
        return ("<%s: %s>") % (self.__class__.__name__, str(self))

class Register(Word): pass

class Memory(object):
    def __init__(self, size, wordsize):
        self._size = size
        self._wsz  = wordsize
        self._data = [Word(0, sz=self._wsz) for _ in range(size)]

    def set(self, addr, value):
        self._data[addr % self._size] = Word(value, sz=self._wsz)

    def get(self, addr):
        return self._data[int(addr) % self._size]
