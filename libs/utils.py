# coding: utf8

import re

from .const import STANDARD_SPACE


def single_line_input():
    return input(">").strip()


def continue_input(iter_count=1):
    return input(STANDARD_SPACE*iter_count).strip()


def filter_real_codes(codes):
    NOT_REAL_CODES_RE = re.compile(r"(\"|'|\d)+")
    return [
        code
        for code in codes
        if code and not NOT_REAL_CODES_RE.match(code)
    ]


def parse_block(block):
    def parse_code_with_symbols(code, symbols):
        if len(symbols) <= 0:
            return [code.strip()]
        if code.find(symbols[0]) == -1:
            return parse_code_with_symbols(code, symbols[1:])

        codes = [code]
        for c in code.split(symbols[0]):
            codes.extend(
                parse_code_with_symbols(c.strip(') '), symbols[1:])
            )
        return codes

    SPLIT_SYMBOL = [',', ';', '(', '=', '+', '-', '*', '/']
    codes = []
    for code in block.get_codes():
        codes.extend(parse_code_with_symbols(code, SPLIT_SYMBOL))

    return filter_real_codes(codes)
