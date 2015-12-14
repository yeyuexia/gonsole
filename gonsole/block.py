# coding: utf8

import re

from .const import STANDARD_SPACE

from .utils import continue_input


class KeyboardInterruptInBlock(Exception):
    pass


class BlockGenerator:
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
        code = continue_input(iter_count)
        while not code.endswith(end_symbol):
            block.append(self.generate(code, iter_count + 1))
            code = continue_input(iter_count)
        block.append(code)


class Block:
    ASSIGNMENT_RE = re.compile(r"(?P<vari>\w+)[ ]*:=[^=]+")
    VARIABLE_DECLARE_RE = re.compile("(var|const) (?P<vari>\w+) ")
    TYPE_DEFINE_RE = re.compile("type (?P<vari>\w+) *")

    def __init__(self, code):
        self.codes = [code]

    def append(self, code):
        self.codes.append(code)

    def inflate_space(self, code, indent):
        return STANDARD_SPACE * indent + code

    def get_declared_varis(self):
        for code in self.get_codes():
            result = self._get_declared_vari(code)
            if result:
                yield result.group("vari")

    def get_codes(self):
        codes = []
        for code in self.codes:
            if isinstance(code, Block):
                codes.extend(code.get_codes())
            else:
                codes.append(code)
        return codes

    def deflate(self, indent=0):
        codes = []
        for code in self.codes:
            if isinstance(code, Block):
                codes.extend(code.deflate(indent+1))
            else:
                codes.append(self.inflate_space(code, indent))
        return codes

    def _filter_real_codes(self, codes):
        NOT_REAL_CODES_RE = re.compile(r"(\"|'|\d)+")
        return [
            code
            for code in codes
            if code and not NOT_REAL_CODES_RE.match(code)
        ]

    def _get_declared_vari(self, code):
        return (
            self.VARIABLE_DECLARE_RE.match(code) or
            self.ASSIGNMENT_RE.match(code) or
            self.TYPE_DEFINE_RE.match(code)
        )

    def is_declared(self):
        return len(self.codes) == 1 and self._get_declared_vari(
            self._filter_real_codes(self.codes[0].split(";"))[-1]
        ) and True

    def _parse_code_with_symbols(self, code, symbols):
        if len(symbols) <= 0:
            return [code.strip()]
        if code.find(symbols[0]) == -1:
            return self._parse_code_with_symbols(code, symbols[1:])

        codes = [code]
        for c in code.split(symbols[0]):
            codes.extend(
                self._parse_code_with_symbols(c.strip(') '), symbols[1:])
            )
        return codes

    def parse_to_codes(self):
        SPLIT_SYMBOL = [',', ';', '(', '=', '+', '-', '*', '/']
        codes = []
        for code in self.get_codes():
            codes.extend(self._parse_code_with_symbols(code, SPLIT_SYMBOL))

        return self._filter_real_codes(codes)
