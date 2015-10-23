# coding: utf8

from .const import STANDARD_SPACE


def single_line_input():
    return input(">").strip()


def continue_input(iter_count=1):
    return input(STANDARD_SPACE*iter_count).strip()
