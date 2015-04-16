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

class Constant(object):

    def __init__(self, val):
        self.val = val

    def asm(self):
        return self.val

class Operand(object):
    def __init__(self, addr_mode, register=0, constant=None):
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

    def __repr__(self):
        return '<Operand %s>' % self

    def asm(self):
        return self.addr_mode << 3 | self.register

class Instruction(object):
    opcode = 0
    def __str__(self):
        return "%s" % self.__class__.__name__.upper()
    def __repr__(self):
        return '<Insn %s>' % self

class BinaryInsn(Instruction):
    operands = 2

    def __init__(self, dest_op, src_op):
        self.dest_op = dest_op
        self.src_op  = src_op
        self.opns = [self.dest_op, self.src_op]

    def __str__(self):
        return "%s %s, %s" % (self.__class__.__name__.upper(), self.dest_op, self.src_op)

    def asm(self):
        bs = self.opcode << 12 | self.dest_op.asm() << 6 | self.src_op.asm()

        if self.dest_op.constant is not None:
            bs <<= 16
            bs |= self.dest_op.constant
        if self.src_op.constant is not None:
            bs <<= 16
            bs |= self.src_op.constant

        return bs

class UnaryDestInsn(Instruction):
    operands = 1

    def __init__(self, dest_op):
        self.dest_op = dest_op
        self.opns = [self.dest_op]
    def __str__(self):
        return "%s %s" % (self.__class__.__name__.upper(), self.dest_op)

    def asm(self):
        bs = self.opcode << 12 | self.dest_op.asm() << 6

        if self.dest_op.constant is not None:
            bs <<= 16
            bs |= self.dest_op.constant

        return bs

class UnarySrcInsn(Instruction):
    operands = 1

    def __init__(self, src_op):
        self.src_op = src_op
        self.opns = [self.src_op]
    def __str__(self):
        return "%s %s" % (self.__class__.__name__.upper(), self.src_op)

    def asm(self):

        bs = self.opcode << 12 | self.src_op.asm()

        if self.src_op.constant is not None:
            bs <<= 16
            bs |= self.src_op.constant

        return bs

class CondJmpInsn(Instruction):
    operands = 1

    def __init__(self, shift):
        self.shift = shift
        self.opns = [self.shift]
    def __str__(self):
        return "%s %s" % (self.__class__.__name__.upper(), self.shift)

    def asm(self):
        return 0b1111 << 12 | self.opcode << 8 | (self.shift.constant & 0b11111111)

class NullaryInsn(Instruction):
    operands = 0

    def __init__(self):
        self.opns = []
        
    def asm(self):
        return self.opcode << 12

class Directive(Instruction): pass
class UnaryDtv(Directive):
    operands = 1

    def __init__(self, arg):
        self.arg = arg
        self.opns = [self.arg]

    def __str__(self):
        return "%s %s" % (self.__class__.__name__.upper(), self.arg)

class Mov(BinaryInsn):    opcode = 0b0001
class Add(BinaryInsn):    opcode = 0b0010
class Sub(BinaryInsn):    opcode = 0b0011
class And(BinaryInsn):    opcode = 0b0100
class Or(BinaryInsn):     opcode = 0b0101
class Cmp(BinaryInsn):    opcode = 0b0110
class Addc(BinaryInsn):   opcode = 0b1101

class Neg(UnaryDestInsn): opcode = 0b1000
class Not(UnaryDestInsn): opcode = 0b1001

class Jmp(UnarySrcInsn):  opcode = 0b1010
class Call(UnarySrcInsn): opcode = 0b1011

class Ret(NullaryInsn):   opcode = 0b1100

class UnknownCondJmp(Instruction): opcode = 0b1111

class Je(CondJmpInsn):    opcode = 0b0001
class Jne(CondJmpInsn):   opcode = 0b1001
class Jle(CondJmpInsn):   opcode = 0b0010
class Jg(CondJmpInsn):    opcode = 0b1010
class Jl(CondJmpInsn):    opcode = 0b0011
class Jge(CondJmpInsn):   opcode = 0b1011
class Jleu(CondJmpInsn):  opcode = 0b0100
class Jgu(CondJmpInsn):   opcode = 0b1100
class Jcs(CondJmpInsn):   opcode = 0b0101
class Jneg(CondJmpInsn):  opcode = 0b0110
class Jvs(CondJmpInsn):   opcode = 0b0111

class Dw(UnaryDtv):
    def asm(self):
        return self.arg.constant
