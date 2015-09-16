# coding: utf8

from os import path

from libs.console import GoCodeCache
from libs.utils import single_line_input

CURRENT_PATH = path.dirname(path.realpath(__file__))


def run_console():
    cache = GoCodeCache(CURRENT_PATH)
    while True:
        cache.run(single_line_input())


if __name__ == '__main__':
    run_console()