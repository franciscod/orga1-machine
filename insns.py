# -*- coding: utf-8 -*-

class InvalidInstruction(Exception): pass
class UnknownInstruction(Exception): pass

class AddressingModes(object):
    IMMEDIATE = 0b000
    DIRECT    = 0b001
    INDIRECT  = 0b011
    REGISTER  = 0b100
    IND_REG   = 0b110
    INDEXED   = 0b111

class Instruction(object):
    def __str__(self):
        return "%s" % self.__class__.__name__.upper()

class BinaryInsn(Instruction):
    def __init__(self, dest, src):
        self.dest = dest
        self.src  = src

class UnaryDestInsn(Instruction):
    def __init__(self, dest):
        self.dest = dest

class UnarySrcInsn(Instruction):
    def __init__(self, src):
        self.src = src

class NullaryInsn(Instruction): pass
class CondJmpInsn(Instruction): pass

class Mov(BinaryInsn):    pass
class Add(BinaryInsn):    pass
class Sub(BinaryInsn):    pass
class And(BinaryInsn):    pass

class Call(UnarySrcInsn): pass
class Jmp(UnarySrcInsn):  pass

class Not(UnaryDestInsn): pass
class Neg(UnaryDestInsn): pass

class Addc(BinaryInsn):   pass
class Cmp(BinaryInsn):    pass
class Or(BinaryInsn):     pass
class Ret(NullaryInsn):   pass

# ninguna de estas altera flags
class Je(CondJmpInsn):    pass
class Jne(CondJmpInsn):   pass
class Jle(CondJmpInsn):   pass
class Jg(CondJmpInsn):    pass
class Jl(CondJmpInsn):    pass
class Jge(CondJmpInsn):   pass
class Jleu(CondJmpInsn):  pass
class Jgu(CondJmpInsn):   pass
class Jcs(CondJmpInsn):   pass
class Jneg(CondJmpInsn):  pass
class Jvs(CondJmpInsn):   pass
