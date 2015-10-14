# coding: utf8

import os
import sys
import subprocess

from .block import Block
from .utils import continue_input
from .utils import single_line_input
from .handlers import PackageHandler
from .handlers import FunctionHandler
from .handlers import CodeHandler


class Console:

    def __init__(self, path):
        self.GO_CODE_TEMPLATE = os.path.join(path, 'go_template')
        self.CACHE_FILE_PATH = os.path.join(
            path, 'console', '_cache', 'main.go'
        )

        with open(self.GO_CODE_TEMPLATE) as f:
            self._template = f.read()
        self.codes = CodeHandler()
        self.packages = PackageHandler()
        self.custom_methods = FunctionHandler()

    def run(self):
        while True:
            self._parse_input(single_line_input())

    def _parse_input(self, text):
        if not text:
            return
        if text == "exit":
            sys.exit(0)
        elif text.startswith("import "):
            self.cache_packages(text)
        elif text.startswith("func "):
            self.cache_func(text)
        else:
            self.cache_code(text)
            self.execute()

    def execute(self):
        with open(self.CACHE_FILE_PATH, "w") as f:
            f.write(self.packages.inflate(
                self.custom_methods.inflate(
                    self.codes.inflate(self._template)
                )
            ))
        self._execute()

    def _execute(self):
        out, err = subprocess.Popen(
            ["go", "run", self.CACHE_FILE_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        ).communicate()

        self.parse_output(out, err)

    def parse_output(self, out, err):
        if err:
            err = err.decode("utf8").split("\n")
            print(err[0])
            print(err[1].split(":", 1)[-1])
            self.codes.rollback()
        if out:
            print(out.decode("utf8").rstrip())

    def cache_code(self, code):
        block = self._parse_code(code)
        self.custom_methods.scan_used_method(block)
        self.codes.add(block)

    def wrap(self, code, iter_count=1):
        block = Block(code)
        if code.strip().endswith("{"):
            code = continue_input(iter_count)
            while not code.endswith("}"):
                block.append(self.wrap(code, iter_count + 1))
                code = continue_input(iter_count)
            block.append(code)
        return block

    def _parse_code(self, code):
        block = self.wrap(code)
        self.packages.scan_used_package(block)

        return block

    def cache_func(self, code):
        self.custom_methods.add(self._parse_code(code))

    def _filter_real_codes(self, codes):
        return [code for code in codes if code and not code.startswith('"')]

    def parse_block(self, block):
        def parse_code_with_symbols(code, symbols):
            if len(symbols) <= 0:
                return [code]
            codes = []
            for c in code.split(symbols[0]):
                codes.extend(
                    parse_code_with_symbols(c.strip(')'), symbols[1:])
                )
            return codes

        SPLIT_SYMBOL = [',', ';', '(']
        codes = []
        for code in block.get_codes():
            codes.extend(parse_code_with_symbols(code, SPLIT_SYMBOL))

        return self._filter_real_codes(codes)

    def cache_packages(self, code):
        if code.endswith("("):
            code = continue_input()
            while code != ")":
                self._cache_import(code)
        else:
            self._cache_import(code)

    def _cache_import(self, code):
        package = code.split(" ", 1)[-1].strip(' ,')
        self.packages.add(package)
