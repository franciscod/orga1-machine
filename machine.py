# -*- coding: utf-8 -*-

from storage import Word, Memory, Register
from insns import (AddressingModes, Operand, UnknownInstruction, InvalidInstruction,
    BinaryInsn, UnaryDestInsn, UnarySrcInsn, NullaryInsn, UnknownCondJmp, CondJmpInsn,
    Mov, Add, Sub, And, Or, Cmp, Addc,
    Neg, Not,
    Jmp, Call,
    Ret,
    Je, Jne, Jle, Jg, Jl, Jge, Jleu, Jgu, Jcs, Jneg, Jvs,
)

class Orga1Machine(object):
    WORD_SIZE = 16
    ADDR_SPACE = 0xFFFF
    REGISTER_COUNT = 8
    STACK_SIZE = 0x10

    INSNS = {
        0b0001: Mov,
        0b0010: Add,
        0b0011: Sub,
        0b0100: And,
        0b0101: Or,
        0b0110: Cmp,
        0b1101: Addc,

        0b1000: Neg,
        0b1001: Not,

        0b1010: Jmp,
        0b1011: Call,

        0b1100: Ret,

        0b1111: UnknownCondJmp,
    }

    CONDJMPINSNS = {
        0b0001: Je,
        0b1001: Jne,
        0b0010: Jle,
        0b1010: Jg,
        0b0011: Jl,
        0b1011: Jge,
        0b0100: Jleu,
        0b1100: Jgu,
        0b0101: Jcs,
        0b0110: Jneg,
        0b0111: Jvs,
    }

    def __init__(self):
        """Algo que tiene la máquina de Orga, que no tiene la de Intel,
        es que TODO, TODO arranca en cero."""
        self.R = [Register(0, self.WORD_SIZE) for _ in range(self.REGISTER_COUNT)]
        self.M = Memory(self.ADDR_SPACE, self.WORD_SIZE)

        self.PC = Register(0, 16)
        self.SP = Register(-self.STACK_SIZE, 16)
        self.Z = 0
        self.C = 0
        self.N = 0
        self.V = 0

    def run(self):
        try:
            while True:
                self.step()
        except InvalidInstruction:
            print ("end of execution")

    def step(self):
        w = self._fetch()
        insn = self._decode(w)

        print ("executing %s" % insn)
        self._execute(insn)

    def _fetch(self):
        word = self.M.get(self.PC)
        self.PC.set(int(self.PC) + 1)
        return word

    def _decode(self, word):

        opcode = word.get_bits(4)

        if not opcode in self.INSNS:
            raise InvalidInstruction(word)

        insn = self.INSNS[opcode]

        def got(superclass):
            return issubclass(insn, superclass)

        if got(BinaryInsn):
            dest_op = self._get_dest_operand(word)
            src_op = self._get_src_operand(word)

            if dest_op.addr_mode == AddressingModes.IMMEDIATE and not got(Cmp):
                raise InvalidInstruction(word)

            return insn(dest_op, src_op)

        if got(UnaryDestInsn):
            if word.get_bits(6, 10) != 0:
                raise InvalidInstruction(word)

            dest_op = self._get_dest_operand(word)

            if dest_op.addr_mode == AddressingModes.IMMEDIATE:
                raise InvalidInstruction(word)

            return insn(dest_op)

        if got(UnarySrcInsn):
            if word.get_bits(6, 4) != 0:
                raise InvalidInstruction(word)

            src_op = self._get_src_operand(word)

            return insn(src_op)

        if got(NullaryInsn):
            if word.get_bits(12, 4) != 0:
                raise InvalidInstruction(word)

            return insn()

        if got(UnknownCondJmp):
            subopcode = word.get_bits(4, 4)

            if not subopcode in self.CONDJMPINSNS:
                raise InvalidInstruction(word)

            condjmpinsn = self.CONDJMPINSNS[subopcode]

            return condjmpinsn(Word(word.get_bits(8, 8), 8).extend_sign(16))

        raise UnknownInstruction(word)

    def _get_dest_operand(self, word):
        return self._get_abs_operand(word, 0)

    def _get_src_operand(self, word):
        return self._get_abs_operand(word, 6)

    def _get_abs_operand(self, word, offset):
        addr_mode = word.get_bits(3, offset + 4)
        register_num = word.get_bits(3, offset + 7)
        constant = None

        if addr_mode in (AddressingModes.IMMEDIATE, AddressingModes.DIRECT, AddressingModes.INDIRECT, AddressingModes.INDEXED):
            constant = self._fetch()

        return Operand(addr_mode, register_num, constant)

    def _execute(self, insn):

        def got(superclass):
            return isinstance(insn, superclass)

        fn = self.__class__.__dict__.get('_' + insn.__class__.__name__.lower())

        if got(BinaryInsn):
            return fn(self, self._cast_operand(insn.dest_op), self._cast_operand(insn.src_op))

        if got(UnaryDestInsn):
            return fn(self, self._cast_operand(insn.dest_op))

        if got(UnarySrcInsn):
            return fn(self, self._cast_operand(insn.src_op))

        if got(NullaryInsn):
            return fn(self)

        if got(CondJmpInsn):
            return fn(self, insn.shift)

    def _cast_operand(self, op):
        am = op.addr_mode
        rn = op.register
        k  = op.constant

        if am == AddressingModes.IMMEDIATE:
            return k

        if am == AddressingModes.DIRECT:
            return self.M.get(k)

        if am == AddressingModes.INDIRECT:
            return self.M.get(self.M.get(k))

        if am == AddressingModes.REGISTER:
            return self.R[rn]

        if am == AddressingModes.IND_REG:
            return self.M.get(self.R[rn])

        if am == AddressingModes.INDEXED:
            return self.M.get(k + self.R[rn])

        raise UnknownInstruction()

    def _mov(self, dest, src):
        dest.set(src)

    def _add(self, dest, src):
        self._addc(dest, src, clear_carry=True)

    def _sub(self, dest, src):
        self._neg(src)
        self._addc(dest, src, clear_carry=True)

    def _and(self, dest, src):
        dest.set(int(dest) & int(src))
        self._update_flags(dest)

    def _or(self, dest, src):
        dest.set(int(dest) | int(src))
        self._update_flags(dest)

    def _cmp(self, dest, src):
        self._neg(src)
        self._addc(dest, src, clear_carry=True, only_flags=True)

    def _addc(self, dest, src, clear_carry=False, only_flags=False):
        if clear_carry:
            self.C = 0

        dest_signed = dest.is_signed()
        src_signed = src.is_signed()

        res = int(dest) + int(src) + self.C
        res_w = Word(res, self.WORD_SIZE)
        res_signed = res_w.is_signed()


        self.C = int(res & (2 ** (self.WORD_SIZE + 1)) != 0)
        self.V = int((not (dest_signed == src_signed)) and (res_signed != dest_signed))

        self._update_flags(res_w)

        if only_flags:
            return

        dest.set(res)

    def _neg(self, dest):
        dest.set(- int(dest))
        self._update_flags(dest)

    def _not(self, dest):
        dest.set(dest ^ (2 ** self.WORD_SIZE - 1))
        self._update_flags(dest)

    def _jmp(self, src):
        self.PC.set(src)

    def _call(self, src):
        self.M.get(self.SP).set(self.PC)
        self.SP.set(int(self.SP) - 1)
        self.PC.set(src)

    def _ret(self):
        self.SP.set(self.M.get(int(self.SP) + 1))
        self.PC.set(self.SP)

    def _je(self, shift):
        if self.Z:
            self.__jrel(shift)

    def _jne(self, shift):
        if not self.Z:
            self.__jrel(shift)

    def _jle(self, shift):
        if self.Z or (self.N ^ self.V):
            self.__jrel(shift)

    def _jg(self, shift):
        if not (self.Z or (self.N ^ self.V)):
            self.__jrel(shift)

    def _jl(self, shift):
        if self.N ^ self.V:
            self.__jrel(shift)

    def _jge(self, shift):
        if not (self.N ^ self.V):
            self.__jrel(shift)

    def _jleu(self, shift):
        if self.C or self.Z:
            self.__jrel(shift)

    def _jgu(self, shift):
        if not (self.C or self.Z):
            self.__jrel(shift)

    def _jcs(self, shift):
        if self.C:
            self.__jrel(shift)

    def _jneg(self, shift):
        if self.N:
            self.__jrel(shift)

    def _jvs(self, shift):
        if self.V:
            self.__jrel(shift)

    def __jrel(self, shift):
        self.PC.set(int(self.PC) + int(shift))

    def _update_flags(self, word):
        self.Z = int(word) == 0
        self.N = word.is_signed()
