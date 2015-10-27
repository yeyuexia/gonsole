# coding: utf8

import os
import sys
import subprocess

from .block import BlockGenerator
from .utils import continue_input
from .utils import single_line_input
from .handlers import AssignmentManager
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
        self.assignment_manager = AssignmentManager.instance()
        self.block_generator = BlockGenerator()

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
            self.cache_code(text)
            try:
                self.prepare()
            except NotDeclaredError:
                print("parameter not declared")
                self._rollback()

            self.execute()

    def export(self, command):
        self._write_to_file(command[7:].strip())

    def prepare(self):
        self.custom_methods.scan_used(self.codes.blocks)
        self.packages.scan_used(
            self.codes.blocks + self.custom_methods.methods
        )
        if (
            self.codes.blocks and
            not self.assignment_manager.get_all_assigned()
        ):
            raise NotDeclaredError
        else:
            self._write_to_file(self.CACHE_FILE_PATH)

    def _write_to_file(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.packages.inflate(
                self.custom_methods.inflate(
                    self.codes.inflate(self._template)
                )
            ))

    def execute(self):
        out, err = subprocess.Popen(
            ["go", "run", self.CACHE_FILE_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        ).communicate()

        self._parse_output(out, err)
        self.assignment_manager.clear()

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
        self.codes.add(self.block_generator.generate(code))

    def cache_func(self, code):
        self.custom_methods.add(self.block_generator.generate(code))

    def _filter_real_codes(self, codes):
        return [code for code in codes if code and not code.startswith('"')]

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
