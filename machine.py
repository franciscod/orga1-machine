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
            raise InvalidInstruction()

        insn = self.INSNS[opcode]

        def got(superclass):
            return issubclass(insn, superclass)

        if got(BinaryInsn):
            dest = self._get_dest_operand(word)
            src = self._get_src_operand(word)
            return insn(dest, src)

        if got(UnaryDestInsn):
            if word.get_bits(6, 10) != 0:
                raise InvalidInstruction()

            dest = self._get_dest_operand(word)

            return insn(dest)

        if got(UnarySrcInsn):
            if word.get_bits(6, 4) != 0:
                raise InvalidInstruction()

            src = dest = self._get_src_operand(word)

            return insn(src)

        if got(NullaryInsn):
            if word.get_bits(12, 4) != 0:
                raise InvalidInstruction()

            return insn()

        # should be unreachable anyway
        raise UnknownInstruction()

    def _get_dest_operand(self, word):
        return self._get_operand(word.get_bits(3, 4), word.get_bits(3, 7))

    def _get_src_operand(self, word):
        return self._get_operand(word.get_bits(3, 10), word.get_bits(3, 13))

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

        raise InvalidInstruction()

    def _execute(self, insn):

        def got(superclass):
            return isinstance(insn, superclass)


        if got(Mov):
            insn.dest.set(insn.src)

        if got(Add):
            dest_signed = insn.dest.is_signed()
            src_signed = insn.src.is_signed()

            res = int(insn.dest) + int(insn.src)
            res_signed = Word(res, self.WORD_SIZE).is_signed()

            self.Z = int(res % (2 ** self.WORD_SIZE) == 0)
            self.C = int(res & (2 ** (self.WORD_SIZE + 1)) != 0)
            self.V = int((not (dest_signed == src_signed)) and (res_signed != dest_signed))
            self.N = res_signed

            insn.dest.set(res)

        if got(Jmp):
            self.PC.set(insn.src)
"""
            # sub
            def execute(self):
                self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] - self.orig[VAL]
                # faltan flags

        #and
            def execute(self):
                self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] & self.orig[VAL]
                # faltan flags


            #or
            def execute(self):
                self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] | self.orig[VAL]
                # faltan flags


            #cmp
            def execute(self):
                # faltan flags
                pass


            #addc
            def execute(self):
                self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] + self.orig[VAL] + self.orga.C
                # faltan flags


            #neg
            def execute(self):
                self.addr[MEM][self.addr[ADDR]] = 0 - self.addr[VAL]
                # faltan flags


            #not
            def execute(self):
                self.addr[MEM][self.addr[ADDR]] = 0xFFFF ^ self.addr[VAL]
                # faltan flags



            #call
            def execute(self):
                self.orga.M[self.orga.SP] = self.orga.PC
                self.orga.SP -= 1
                self.orga.SP %= 0xFFFF
                self.orga.PC = self.addr[VAL]
                # no altera flags

            #ret
            def execute(self):
                self.orga.SP += 1
                self.orga.SP %= 0xFFFF
                self.orga.PC = self.orga.SP
                # no altera flags
        """
