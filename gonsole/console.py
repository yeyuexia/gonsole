# coding: utf8

import os
import re
import sys
import subprocess

from .const import PRINTLN, GO_TEMPLATE
from .block import BlockGenerator
from .utils import post_to_playground
from .utils import continue_input
from .utils import single_line_input
from .handlers import AssignmentManager
from .handlers import CodeHandler
from .handlers import PackageHandler
from .handlers import FunctionHandler
from .exceptions import NotDeclaredError


class Console:
    DIRECT_COMMAND_RE = re.compile(r"^(\d|\"|')+")

    def __init__(self):
        self.CACHE_FILE_PATH = self._generate_file_path()
        self._template = GO_TEMPLATE
        self.codes = CodeHandler()
        self.packages = PackageHandler()
        self.custom_methods = FunctionHandler()
        self.assignment_manager = AssignmentManager.instance()
        self.block_generator = BlockGenerator()

    def _generate_file_path(self):
        file_path = os.path.join(
            "", "tmp", "console", "_cache"
        )
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        return os.path.join(file_path, "main.go")

    def run(self):
        while True:
            try:
                self.parse_input(single_line_input())
            except KeyboardInterrupt:
                self._exit()

    def _exit(self):
        print("exit")
        sys.exit(0)

    def parse_input(self, text):
        if not text:
            return

        execute_content = None
        if self.DIRECT_COMMAND_RE.match(text):
            execute_content = self.direct_command(text)
        elif text == "exit":
            self._exit()
        elif text == "playground":
            self.export_to_playground()
        elif text.startswith("export "):
            self.export(text)
        elif text.startswith("import "):
            self.cache_packages(text)
        elif text.startswith("func "):
            self.cache_func(text)
        else:
            self.cache_code(text)
            try:
                execute_content = self.prepare()
            except NotDeclaredError:
                print("parameter not declared")
                self._rollback()

        if execute_content:
            self._write_to_file(self.CACHE_FILE_PATH, execute_content)
            self.execute()

    def direct_command(self, command):
        return self._template.replace(
            "{%import_area%}", "\"fmt\""
        ).replace(
            "{%func_area%}", ""
        ).replace(
            "{%code_area%}", PRINTLN.format(command)
        )

    def export(self, command):
        self._write_to_file(command[7:].strip(), self.prepare())

    def export_to_playground(self):
        print(post_to_playground(self.prepare()))

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
        return self._inflate()

    def _inflate(self):
        return self.packages.inflate(
            self.custom_methods.inflate(
                self.codes.inflate(self._template)
            )
        )

    def _write_to_file(self, file_path, content):
        with open(file_path, "w") as f:
            f.write(content)

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
        error_reason, detail = err.decode("utf8").split("\n")
        print(error_reason)
        print(detail.split(":", 1)[-1])

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
        block = self.block_generator.generate(code)
        self.codes.add(block)
        return not block.is_declared()

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
