# coding: utf8

import re

from gonsole.utils import inflate_space
from .codes import filter_real_codes
from .declared import (
    get_declared_varis,
    get_declared_symbol,
    get_batch_declared_varis
)


class KeyboardInterruptInBlock(Exception):
    pass


class BlockGenerator:
    def __init__(self, continue_input):
        self.continue_input = continue_input

    def generate(self, code, iter_count=1):
        try:
            block = Block(code)
            if code.strip().endswith("{"):
                self.continuing_get_input("}", block, iter_count)
            elif code.strip().endswith("("):
                self.continuing_get_input(")", block, iter_count)
        except KeyboardInterrupt:
            raise KeyboardInterruptInBlock()
        return block

    def continuing_get_input(self, end_symbol, block, iter_count):
        code = self.continue_input(iter_count)
        while not code.endswith(end_symbol):
            block.append(self.generate(code, iter_count + 1))
            code = self.continue_input(iter_count)
        block.append(code)


class Block:
    VARIABLE_DECLARE_RE = re.compile("(var|const) (?P<varis>[_\w]+(, *[_\w]+)*)( [_\w]+)?(( )*=)?[^(]*")
    BATCH_VARIABLE_DECLARED_RE = re.compile(r"(var|const)[ ]*\(")
    TYPE_DEFINE_RE = re.compile("type (?P<var>\w+) *")
    DECLARE_KEYWORD = re.compile("^(?P<keyword>(const|var|type)) ")
    BATCH_DECLARE_RE = re.compile("(?P<var>[_\w]+) *=")

    def __init__(self, code):
        self.codes = [code]

    def append(self, code):
        self.codes.append(code)

    def is_func(self):
        return self.codes[0].startswith("func ")

    def get_codes(self):
        codes = []
        for code in self.codes:
            (
                codes.extend(code.get_codes())
                if isinstance(code, Block) else codes.append(code)
            )
        return codes

    def deflate(self, indent=0):
        codes = []
        for code in self.codes:
            (
                codes.extend(code.deflate(indent+1))
                if isinstance(code, Block)
                else codes.append(inflate_space(code, indent))
            )
        return codes

    @classmethod
    def _get_batch_declared_var(cls, code):
        return cls.BATCH_DECLARE_RE.match(code).group("var")

    def get_declared_varis(self):
        varis = []
        varis.extend(get_batch_declared_varis(self.codes))
        for code in self.codes:
            varis.extend(get_declared_varis(code))
        return varis

    def is_declared(self):
        return get_declared_symbol(
            filter_real_codes(self.codes[0].split(";"))[-1]
        ) and True or False

    @classmethod
    def _parse_code_with_symbols(cls, code, symbols):
        if len(symbols) <= 0:
            return [code.strip()]
        if code.find(symbols[0]) == -1:
            return cls._parse_code_with_symbols(code, symbols[1:])

        codes = [code]
        for c in code.split(symbols[0]):
            codes.extend(
                cls._parse_code_with_symbols(c.strip(') '), symbols[1:])
            )
        return codes

    def parse_to_codes(self):
        SPLIT_SYMBOL = [' ', ',', ';', '(', '=', '+', '-', '*', '/']
        codes = []
        for code in self.get_codes():
            codes.extend(self._parse_code_with_symbols(code, SPLIT_SYMBOL))

        return filter_real_codes(codes)
