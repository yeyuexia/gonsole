# coding: utf8

import re

from .const import STANDARD_SPACE


class Block:
    IS_ASSIGNMENT_RE = re.compile(r"(?P<vari>\w+)[ ]*:=[^=]+")
    VARIABLE_DECLARE_RE = re.compile("(var|const) (?P<vari>\w+) ")

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
        for code in self.codes:
            if isinstance(code, Block):
                yield from code.get_codes()
            else:
                yield code

    def deflate(self, indent=0):
        for code in self.codes:
            if isinstance(code, Block):
                yield from code.deflate(indent+1)
            else:
                yield self.inflate_space(code, indent)

    def _filter_real_codes(self, codes):
        NOT_REAL_CODES_RE = re.compile(r"(\"|'|\d)+")
        return [
            code
            for code in codes
            if code and not NOT_REAL_CODES_RE.match(code)
        ]

    def _get_declared_vari(self, code):
        return self.VARIABLE_DECLARE_RE.match(code) or self.IS_ASSIGNMENT_RE.match(code)

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
