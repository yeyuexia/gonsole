# coding: utf8

import os
import sys
import subprocess

from .utils import continue_input
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
        self.custom_funcs = FunctionHandler()

    def run(self, command):
        command and self._parse_input(command)

    def _parse_input(self, command):
        if command == "exit":
            sys.exit(0)
        elif command.startswith("import "):
            self.cache_packages(command)
        elif command.startswith("func "):
            self.cache_func(command)
        else:
            self.cache_code(command)
            self.execute()

    def execute(self):
        with open(self.CACHE_FILE_PATH, "w") as f:
            f.write(self.packages.inflate(
                self.custom_funcs.inflate(
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
        if out:
            print(out.decode("utf8").rstrip())

    def cache_code(self, code):
        self.packages.scan_used_package(code)
        self.codes.add(code)

    def cache_func(self, code):
        pass

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


