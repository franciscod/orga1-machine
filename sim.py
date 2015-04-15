# TODO: modelo para una pos de memoria, con get y set
# TODO: aritmetica de precision fija

class InvalidInstruction(Exception):
    pass

class AddrModes(object): # FIXME: poor man's enum
    IMMEDIATE = 0b000
    DIRECT    = 0b001
    INDIRECT  = 0b011
    REGISTER  = 0b100
    IND_REG   = 0b110
    INDEXED   = 0b111

class Op(object):
    def __init__(self):
        self.name = self._get_name().upper()

    def _get_name(self):
        cn = self.__class__.__name__

        if cn == 'Op':
            return '_unset'

        if cn[-2:] == 'Op':
            return '_' + cn[:-2]

        if cn[:2] == 'Op':
            return cn[2:]

class ValidOp(Op):
    def __init__(self, orga, word):
        super().__init__()
        self.orga = orga
        self.word = word

    def _read_addr_value(self, addrcode): # FIXME: esto hace magia, no va acá, podría ser otra clase
        achigh = addrcode >> 3
        aclow = addrcode & 0b111

        if achigh == AddrModes.IMMEDIATE:
            assert(aclow == 0)
            v = self.orga.fetch()
            return None, None, v

        if achigh == AddrModes.DIRECT:
            assert(aclow == 0)
            w = self.orga.M
            addr = self.orga.fetch()

        if achigh == AddrModes.INDIRECT:
            assert(aclow == 0)
            w = self.orga.M
            addr = self.orga.M[self.orga.fetch()]

        if achigh == AddrModes.REGISTER:
            w = self.orga.R
            addr = aclow

        if achigh == AddrModes.IND_REG:
            w = self.orga.M
            addr = self.orga.R[aclow]

        if achigh == AddrModes.INDEXED:
            w = self.orga.M
            addr = (self.orga.R[aclow] + self.orga.fetch()) % 0xFFFF

        return w, addr, w[addr]
#              \    \     \
#              \    \     \
MEM  = 0 # ----/    \     \
ADDR = 1 # --------/      \
VAL  = 2 # --------------/


# type1
class BinaryOp(ValidOp):
    def __init__(self, orga, word):
        super().__init__(orga, word)
        self.dest = self._read_addr_value((self.word >> 6) & 0b111111)
        self.orig = self._read_addr_value(self.word & 0b111111)

# type2a
class UnaryDestOp(ValidOp):
    def __init__(self, orga, word):
        super().__init__(orga, word)
        self.addr = self._read_addr_value((self.word >> 6) & 0b111111)
        assert ((self.word & 0b111111) == 0)

# type2b
class UnaryOrigOp(ValidOp):
    def __init__(self, orga, word):
        super().__init__(orga, word)
        self.addr = self._read_addr_value(self.word & 0b111111)
        assert (((self.word >> 6) & 0b111111) == 0)

# type3
class AryOp(ValidOp):
    def __init__(self, orga, word):
        super().__init__(orga, word)
        assert ((self.word & 0b111111111111) == 0)

# type4
class CondJmpOp(ValidOp):
    def __init__(self, orga, word):
        super().__init__(orga, word)

class OpMov(BinaryOp):
    def execute(self):
        self.dest[MEM][self.dest[ADDR]] = self.orig[VAL]
        # no altera flags

class OpAdd(BinaryOp):
    def execute(self):
        sg_dest = int(self.dest[VAL] & 0x8000 == 1)
        sg_orig = int(self.orig[VAL] & 0x8000 == 1)

        self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] + self.orig[VAL]
        sg_res = int(self.dest[MEM][self.dest[ADDR]] & 0x8000 == 1)

        self.orga.Z = int(self.dest[MEM][self.dest[ADDR]] == 0)
        self.orga.C = int(self.dest[MEM][self.dest[ADDR]] == 0x10000)
        self.orga.V = int((not (sg_dest == sg_orig)) and (sg_res != sg_dest))
        self.orga.N = int(self.dest[MEM][self.dest[ADDR]] & 0x8000 == 1)

        self.dest[MEM][self.dest[ADDR]] %= 0xFFFF

class OpSub(BinaryOp):
    def execute(self):
        self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] - self.orig[VAL]
        # faltan flags

class OpAnd(BinaryOp):
    def execute(self):
        self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] & self.orig[VAL]
        # faltan flags

class OpOr(BinaryOp):
    def execute(self):
        self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] | self.orig[VAL]
        # faltan flags

class OpCmp(BinaryOp):
    def execute(self):
        # faltan flags
        pass

class OpAddc(BinaryOp):
    def execute(self):
        self.dest[MEM][self.dest[ADDR]] = self.dest[VAL] + self.orig[VAL] + self.orga.C
        # faltan flags

class OpNeg(UnaryDestOp):
    def execute(self):
        self.addr[MEM][self.addr[ADDR]] = 0 - self.addr[VAL]
        # faltan flags

class OpNot(UnaryDestOp):
    def execute(self):
        self.addr[MEM][self.addr[ADDR]] = 0xFFFF ^ self.addr[VAL]
        # faltan flags

class OpJmp(UnaryOrigOp):
    def execute(self):
        self.orga.PC = self.addr[VAL]
        # no altera flags

class OpCall(UnaryOrigOp):
    def execute(self):
        self.orga.M[self.orga.SP] = self.orga.PC
        self.orga.SP -= 1
        self.orga.SP %= 0xFFFF
        self.orga.PC = self.addr[VAL]
        # no altera flags

class OpRet(AryOp):
    def execute(self):
        self.orga.SP += 1
        self.orga.SP %= 0xFFFF
        self.orga.PC = self.orga.SP
        # no altera flags


# ninguna de estas altera flags
class OpJe(CondJmpOp):
    pass

class OpJne(CondJmpOp):
    pass

class OpJle(CondJmpOp):
    pass

class OpJg(CondJmpOp):
    pass

class OpJl(CondJmpOp):
    pass

class OpJge(CondJmpOp):
    pass

class OpJleu(CondJmpOp):
    pass

class OpJgu(CondJmpOp):
    pass

class OpJcs(CondJmpOp):
    pass

class OpJneg(CondJmpOp):
    pass

class OpJvs(CondJmpOp):
    pass


class Orga1(object):
    WORDSIZE = 16
    ADDR_SPACE = 0xFFFF
    REGISTER_COUNT = 8

    PC = 0
    SP = 0xFFEF
    IR = 0

    Z = 0
    C = 0
    V = 0
    N = 0

    OPS = {
        0b0001: OpMov,
        0b0010: OpAdd,
        0b0011: OpSub,
        0b0100: OpAnd,
        0b0101: OpOr,
        0b0110: OpCmp,
        0b1101: OpAddc,

        0b1000: OpNeg,
        0b1001: OpNot,

        0b1010: OpJmp,
        0b1011: OpCall,

        0b1100: OpRet,

        0b1111: CondJmpOp,
    }

    def __init__(self):
        """Algo que tiene la máquina de Orga, que no tiene la de Intel,
        es que TODO, TODO arranca en cero."""

        self.M = [0 for _ in range(self.ADDR_SPACE)]
        self.R = [0 for _ in range(self.REGISTER_COUNT)]

    def fetch(self):
        return self.M[self._incrd_pc()]

    def _incrd_pc(self):
        oldPC = self.PC

        self.PC += 1
        self.PC %= 0xFFFF

        return oldPC

    def _decode(self, w):
        opcode = w >> 12

        try:
            op = Orga1.OPS[opcode]

        except KeyError as e:
            raise InvalidInstruction()

        return op(self, w)

    def step(self):
        print (self.Z, self.C, self.V, self.N)

        w = self.fetch()
        op = self._decode(w)

        op.execute()

        print (self.Z, self.C, self.V, self.N)

        return op


    def load(self, file):
        with file as f:
            i = 0

            while True:
                hex = file.read(4)
                if hex == '\n':
                    break

                self.M[i] = int(hex, 16)
                i += 1
import sys

maq = Orga1()
maq.load(open(sys.argv[1]))
