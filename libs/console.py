# coding: utf8

import os
import sys
import subprocess

from .block import Block
from .utils import continue_input
from .utils import single_line_input
from .handlers import CodeHandler
from .handlers import PackageHandler
from .handlers import FunctionHandler
from .exceptions import NotDeclaredError


class Console:

    def __init__(self, path):
        self.CACHE_FILE_PATH = self._generate_file_path(path)
        self.GO_CODE_TEMPLATE = os.path.join(path, 'go_template')

        with open(self.GO_CODE_TEMPLATE) as f:
            self._template = f.read()
        self.codes = CodeHandler()
        self.packages = PackageHandler()
        self.custom_methods = FunctionHandler()

    def _generate_file_path(self, path):
        file_path = os.path.join(
            path, 'console', '_cache'
        )
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        return os.path.join(file_path, "main.go")

    def run(self):
        while True:
            self.parse_input(single_line_input())

    def parse_input(self, text):
        if not text:
            return
        if text == "exit":
            sys.exit(0)
        elif text.startswith("export "):
            self.export(text)
        elif text.startswith("import "):
            self.cache_packages(text)
        elif text.startswith("func "):
            self.cache_func(text)
        else:
            try:
                self.cache_code(text)
            except NotDeclaredError:
                print("parameter not declared")
                self._rollback()
            self.execute()

    def export(self, command):
        self._write_to_file(command[7:].strip())

    def execute(self):
        self.custom_methods.scan_used(self.codes.blocks)
        self.packages.scan_used(
            self.codes.blocks + self.custom_methods.methods
        )
        self._write_to_file(self.CACHE_FILE_PATH)
        self._execute()

    def _write_to_file(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.packages.inflate(
                self.custom_methods.inflate(
                    self.codes.inflate(self._template)
                )
            ))

    def _execute(self):
        out, err = subprocess.Popen(
            ["go", "run", self.CACHE_FILE_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        ).communicate()

        self._parse_output(out, err)

    def _parse_err_message(self, err):
        err = err.decode("utf8").split("\n")
        print(err[0])
        print(err[1].split(":", 1)[-1])

    def _rollback(self):
        self.codes.rollback()

    def _parse_output(self, out, err):
        if err:
            self._parse_err_message(err)
            self._rollback()
        if out:
            print(out.decode("utf8").rstrip())

    def cache_code(self, code):
        self.codes.clear()
        self.codes.add(self.wrap(code))

    def wrap(self, code, iter_count=1):
        block = Block(code)
        if code.strip().endswith("{"):
            code = continue_input(iter_count)
            while not code.endswith("}"):
                block.append(self.wrap(code, iter_count + 1))
                code = continue_input(iter_count)
            block.append(code)
        return block

    def cache_func(self, code):
        self.custom_methods.add(self.wrap(code))

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
