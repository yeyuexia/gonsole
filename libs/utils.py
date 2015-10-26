# coding: utf8

import sys

from .const import STANDARD_SPACE

IS_PY3 = sys.version_info[0] == 3


def single_line_input():
    return compatibility_input(">").strip()


def continue_input(iter_count=1):
    return compatibility_input(STANDARD_SPACE*iter_count).strip()


def compatibility_input(output):
    if IS_PY3:
        return input(output)
    else:
        return raw_input(output)
