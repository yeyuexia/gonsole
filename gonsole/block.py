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
    VARIABLE_DECLARE_RE = re.compile("(var|const) (?P<varis>[_\w]+(, *[_\w]+)*)( [_\w]+)?(( )*=)?[^(]*")
    BATCH_VARIABLE_DECLARED_RE = re.compile(r"(var|const)[ ]*\(")
    TYPE_DEFINE_RE = re.compile("type (?P<var>\w+) *")
    DECLARE_KEYWORD = re.compile("^(?P<keyword>(const|var|type)) ")
    BATCH_DECLARE_RE = re.compile("(?P<var>[_\w]+) *=")

    def __init__(self, code):
        self.codes = [code]

    def append(self, code):
        self.codes.append(code)

    @classmethod
    def inflate_space(cls, code, indent):
        return STANDARD_SPACE * indent + code

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
                else codes.append(self.inflate_space(code, indent))
            )
        return codes

    @classmethod
    def _filter_real_codes(cls, codes):
        NOT_REAL_CODES_RE = re.compile(r"(\"|'|\d)+")
        return [
            code
            for code in codes
            if code and not NOT_REAL_CODES_RE.match(code)
        ]

    @classmethod
    def get_declared_symbol_or_keyword(cls, code):
        if ":=" in code:
            return ":="
        result = cls.DECLARE_KEYWORD.match(code)
        return result.group("keyword") if result else None

    @classmethod
    def _get_declared_varis(cls, code):

        def get_vari_by_keyword_var_or_const(code):
            varis = cls.VARIABLE_DECLARE_RE.match(code).group("varis")
            return [var.strip() for var in varis.split(",") if var]

        return {
            ":=": lambda code: [var.strip() for var in code.split(":=")[0].split(",") if var],
            "var": lambda code: get_vari_by_keyword_var_or_const(code),
            "const": lambda code: get_vari_by_keyword_var_or_const(code),
            "type": lambda code: [cls.TYPE_DEFINE_RE.match(code).group("var")],
            None: lambda x: None
        }.get(cls.get_declared_symbol_or_keyword(code))(code)

    @classmethod
    def _get_batch_declared_var(cls, code):
        return cls.BATCH_DECLARE_RE.match(code).group("var")

    def get_declared_varis(self):
        varis = []
        codes = self.codes[0].split(";")
        if self.BATCH_VARIABLE_DECLARED_RE.match(codes[-1]):
            varis.extend(
                [self._get_batch_declared_var(var.strip())
                    for var in self.codes[1].get_codes()]
            )
        for code in self._filter_real_codes(codes):
            _varis = self._get_declared_varis(code)
            if _varis:
                varis.extend(_varis)
        return varis

    def is_declared(self):
        return self.get_declared_symbol_or_keyword(
            self._filter_real_codes(self.codes[0].split(";"))[-1]
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
        SPLIT_SYMBOL = [',', ';', '(', '=', '+', '-', '*', '/']
        codes = []
        for code in self.get_codes():
            codes.extend(self._parse_code_with_symbols(code, SPLIT_SYMBOL))

        return self._filter_real_codes(codes)
