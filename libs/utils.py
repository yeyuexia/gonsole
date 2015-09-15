# coding: utf8

STANDARD_SPACE = "    "


def single_line_input():
    return input(">").strip()


def inflate_space(code):
    return STANDARD_SPACE+code


def continue_input():
    return input(STANDARD_SPACE).strip()


def filter_real_codes(codes):
    return [code for code in codes if code and not code.startswith('"')]


def parse_code(code):
    def parse_code_with_symbols(code, symbols):
        if len(symbols) <= 0:
            return [code]
        codes = []
        for c in code.split(symbols[0]):
            codes.extend(parse_code_with_symbols(c.strip(')'), symbols[1:]))
        return codes

    symbols = [',', ';', '(']
    return filter_real_codes(parse_code_with_symbols(code, symbols))
