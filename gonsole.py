# coding: utf8

from os import path

from libs.console import Console

CURRENT_PATH = path.dirname(path.realpath(__file__))


def run_console():
    cache = Console(CURRENT_PATH)
    cache.run()


if __name__ == '__main__':
    run_console()
