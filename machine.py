# -*- coding: utf-8 -*-

from storage import Word, Memory, Register
from insns import (AddressingModes, UnknownInstruction, InvalidInstruction,
    BinaryInsn, UnaryDestInsn, UnarySrcInsn, NullaryInsn, CondJmpInsn,
    Mov, Add, Sub,
    And, Or, Cmp,
    Addc, Neg, Not,
    Jmp, Call, Ret,
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

        0b1111: CondJmpInsn,
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
        while True:
            self.step()

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
            dam, dest = self._get_dest_operand(word)
            sam, src = self._get_src_operand(word)

            if dam == AddressingModes.IMMEDIATE and not got(Cmp):
                raise InvalidInstruction(word)

            return insn(dest, src)

        if got(UnaryDestInsn):
            if word.get_bits(6, 10) != 0:
                raise InvalidInstruction(word)

            dam, dest = self._get_dest_operand(word)

            if dam == AddressingModes.IMMEDIATE:
                raise InvalidInstruction(word)

            return insn(dest)

        if got(UnarySrcInsn):
            if word.get_bits(6, 4) != 0:
                raise InvalidInstruction(word)

            sam, src = self._get_src_operand(word)

            return insn(src)

        if got(NullaryInsn):
            if word.get_bits(12, 4) != 0:
                raise InvalidInstruction(word)

            return insn()

        raise UnknownInstruction()

    def _get_dest_operand(self, word):
        return self._get_abs_operand(word, 0)

    def _get_src_operand(self, word):
        return self._get_abs_operand(word, 6)

    def _get_abs_operand(self, word, o):
        addr_mode = word.get_bits(3, o + 4)
        return addr_mode, self._get_operand(addr_mode, word.get_bits(3, o + 7))

    def _get_operand(self, addr_mode, register_num=None):

        if addr_mode == AddressingModes.IMMEDIATE:
            return self._fetch()

        if addr_mode == AddressingModes.DIRECT:
            return self.M.get(self._fetch())

        if addr_mode == AddressingModes.INDIRECT:
            return self.M.get(self.M.get(self._fetch()))

        if addr_mode == AddressingModes.REGISTER:
            return self.R[register_num]

        if addr_mode == AddressingModes.IND_REG:
            return self.M.get(self.R[register_num])

        if addr_mode == AddressingModes.INDEXED:
            return self.M.get(self._fetch() + self.R[register_num])

        raise UnknownInstruction()

    def _execute(self, insn):

        def got(superclass):
            return isinstance(insn, superclass)

        fn = self.__class__.__dict__.get('_' + insn.__class__.__name__.lower())

        if got(BinaryInsn):
            return fn(self, insn.dest, insn.src)

        if got(UnaryDestInsn):
            return fn(self, insn.dest)

        if got(UnarySrcInsn):
            return fn(self, insn.src)

        if got(NullaryInsn):
            return fn(self  )

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

    def _update_flags(self, word):
        self.Z = int(word) == 0
        self.N = word.is_signed()
