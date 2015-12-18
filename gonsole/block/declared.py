# coding: utf8

import re

from .codes import filter_real_codes


VARIABLE_DECLARE_RE = re.compile("(var|const) (?P<varis>[_\w]+(, *[_\w]+)*)( [_\w]+)?(( )*=)?[^(]*")
BATCH_VARIABLE_DECLARED_RE = re.compile(r"(var|const)[ ]*\(")
TYPE_DEFINE_RE = re.compile("type (?P<var>\w+) *")
DECLARE_KEYWORD = re.compile("^(?P<keyword>(const|var|type)) ")
BATCH_DECLARE_RE = re.compile("(?P<var>[_\w]+) *=")


def get_declared_symbol(code):
    if ":=" in code:
        return ":="
    result = DECLARE_KEYWORD.match(code)
    return result.group("keyword") if result else None


def _get_declared_varis(code):

    def get_vari_by_keyword_var_or_const(code):
        varis = VARIABLE_DECLARE_RE.match(code).group("varis")
        return [var.strip() for var in varis.split(",") if var]

    return {
        ":=": lambda code: [var.strip() for var in code.split(":=")[0].split(",") if var],
        "var": lambda code: get_vari_by_keyword_var_or_const(code),
        "const": lambda code: get_vari_by_keyword_var_or_const(code),
        "type": lambda code: [TYPE_DEFINE_RE.match(code).group("var")],
        None: lambda x: None
    }.get(get_declared_symbol(code))(code)


def get_declared_varis(code):
    varis = []
    for c in filter_real_codes(code.split(";")):
        _varis = _get_declared_varis(c)
        if _varis:
            varis.extend(_varis)
    return varis


def get_batch_declared_varis(codes):

    def get_declared_var(cls, code):
        return cls.BATCH_DECLARE_RE.match(code).group("var")

    if BATCH_VARIABLE_DECLARED_RE.match(
        codes[0].rsplit(";", 1)[-1]
    ):
        return [get_declared_var(var.strip())
                for var in codes[1].get_codes()]
    return []
