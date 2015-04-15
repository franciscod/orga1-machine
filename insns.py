# -*- coding: utf-8 -*-

class InvalidOperand(Exception): pass
class InvalidInstruction(Exception): pass
class UnknownInstruction(Exception): pass

class AddressingModes(object):
    IMMEDIATE = 0b000
    DIRECT    = 0b001
    INDIRECT  = 0b011
    REGISTER  = 0b100
    IND_REG   = 0b110
    INDEXED   = 0b111

class Operand(object):
    def __init__(self, addr_mode, register=None, constant=None):
        self.addr_mode = addr_mode
        self.register = register
        self.constant = constant

    def __str__(self):
        if self.addr_mode == AddressingModes.IMMEDIATE:
            return '%s' % self.constant

        if self.addr_mode == AddressingModes.DIRECT:
            return '[%s]' % self.constant

        if self.addr_mode == AddressingModes.INDIRECT:
            return '[[%s]]' % self.constant

        if self.addr_mode == AddressingModes.REGISTER:
            return 'R%d' % self.register

        if self.addr_mode == AddressingModes.IND_REG:
            return '[R%d]' % self.register

        if self.addr_mode == AddressingModes.INDEXED:
            return '[R%d + %s]' % (self.register, self.constant)

class Instruction(object):
    def __str__(self):
        return "%s" % self.__class__.__name__.upper()

class BinaryInsn(Instruction):
    def __init__(self, dest_op, src_op):
        self.dest_op = dest_op
        self.src_op  = src_op

    def __str__(self):
        return "%s %s, %s" % (self.__class__.__name__.upper(), self.dest_op, self.src_op)

class UnaryDestInsn(Instruction):
    def __init__(self, dest_op):
        self.dest_op = dest_op
    def __str__(self):
        return "%s %s" % (self.__class__.__name__.upper(), self.dest_op)

class UnarySrcInsn(Instruction):
    def __init__(self, src_op):
        self.src_op = src_op
    def __str__(self):
        return "%s %s" % (self.__class__.__name__.upper(), self.src_op)

class CondJmpInsn(Instruction):
    def __init__(self, shift):
        self.shift = shift
    def __str__(self):
        return "%s %s" % (self.__class__.__name__.upper(), self.shift)

class NullaryInsn(Instruction):    pass
class UnknownCondJmp(Instruction): pass

class Mov(BinaryInsn):    pass
class Add(BinaryInsn):    pass
class Sub(BinaryInsn):    pass
class And(BinaryInsn):    pass
class Or(BinaryInsn):     pass
class Cmp(BinaryInsn):    pass
class Addc(BinaryInsn):   pass

class Neg(UnaryDestInsn): pass
class Not(UnaryDestInsn): pass

class Jmp(UnarySrcInsn):  pass
class Call(UnarySrcInsn): pass

class Ret(NullaryInsn):   pass

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
