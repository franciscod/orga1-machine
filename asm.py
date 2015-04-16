# -*- coding: utf-8 -*-

from insns import (Operand, AddressingModes, CondJmpInsn,
                    Mov, Add, Sub, And, Or, Cmp, Addc, Neg, Not, Jmp, Call, Ret,
                    Je, Jne, Jle, Jg, Jl, Jge, Jleu, Jgu, Jcs, Jneg, Jvs, Dw)

insns = { insn.__name__.upper(): insn
            for insn in (
                Mov, Add, Sub, And, Or, Cmp, Addc, Neg, Not, Jmp, Call, Ret,
                Je, Jne, Jle, Jg, Jl, Jge, Jleu, Jgu, Jcs, Jneg, Jvs, Dw
            )
        }

def lex(s):
    cs = s.split()
    tag = None

    if cs[0][-1] == ':':
        tag = cs[0][:-1]
        cs = cs[1:]

    if not cs[0] in insns:
        raise SyntaxError("Invalid instruction: " + cs[0])

    _insn = insns[cs[0]]

    cs = ''.join(cs[1:]).split(',')

    opns = [parse_opn(o) for o in cs if parse_opn(o) is not None]


    if len(opns) != _insn.operands:
        raise SyntaxError("Mismatching operand count: expected %d, got: %s" % (_insn.operands, opns))

    insn = _insn(*opns)

    return tag, insn

def parse_opn(o):
    # TODO: indexed addressing mode
    if o == '':
        return None

    if o[0].upper() == 'R':
        return Operand(AddressingModes.REGISTER, register=int(o[1]))

    if o[:2] == '[[':
        o = o.replace(' ', '').replace('[', '').replace(']', '')
        return Operand(AddressingModes.INDIRECT, constant=o)

    if o[:1] == '[':
        o = o.replace(' ', '').replace('[', '').replace(']', '')
        if o[0].upper() == 'R' and len(o) == 2 and '0' <= o[1] <= '7':
            return Operand(AddressingModes.IND_REG, register=int(o[1]))
        return Operand(AddressingModes.DIRECT, constant=o)

    return Operand(AddressingModes.IMMEDIATE, constant=o)



def parse(lines):

    tokens = []
    wc = 0
    tags = {}

    for line in lines:
        tag, token = lex(line)

        if tag:
            tags[tag] = wc

        wc += token_wc(token)

        tokens.append(token)

    pc = 0
    for token in tokens:
        pc += token_wc(token)
        for o in token.opns:
            if o.constant in tags:
                o.constant = tags[o.constant]

            if isinstance(o.constant, str):
                o.constant = int(o.constant, 16)

            if isinstance(token, CondJmpInsn):
                o.constant = o.constant - pc

    return tokens

def token_wc(token):


    wc = 1 # token
    for o in token.opns:
        if o.addr_mode in ( AddressingModes.IMMEDIATE,
                            AddressingModes.INDIRECT,
                            AddressingModes.DIRECT,
                            AddressingModes.INDEXED, ):
            wc += 1 # constant operand

    if isinstance(token, CondJmpInsn):
        wc = 1
    if isinstance(token, Dw):
        wc = 1

    return wc
