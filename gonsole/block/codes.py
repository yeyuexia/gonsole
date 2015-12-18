# coding: utf8

import re


def filter_real_codes(codes):
    NOT_REAL_CODES_RE = re.compile(r"(\"|'|\d)+")
    return [
        code for
        code in codes
        if code and not NOT_REAL_CODES_RE.match(code)
    ]
