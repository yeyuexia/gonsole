# coding: utf8

import os
import subprocess

from .cmd import Cmd
from .const import PRINTLN, GO_TEMPLATE
from .utils import post_to_playground
from .handlers import AssignmentManager
from .handlers import CodeHandler
from .handlers import PackageHandler
from .handlers import FunctionHandler
from .exceptions import NotDeclaredError


class Console(Cmd):

    def __init__(self):
        super(Console, self).__init__()
        self.CACHE_FILE_PATH = self._generate_file_path()
        self._template = GO_TEMPLATE
        self.codes = CodeHandler()
        self.packages = PackageHandler()
        self.custom_methods = FunctionHandler()
        self.assignment_manager = AssignmentManager.instance()

    def _generate_file_path(self):
        file_path = os.path.join(
            "", "tmp", "console", "_cache"
        )
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        return os.path.join(file_path, "main.go")

    def do_playground(self, *args):
        print(post_to_playground(self.prepare()))

    def do_export(self, *args):
        self._write_to_file(args[1], self.prepare())

    def do_import(self, *args):
        if args[-1].endswith("("):
            code = self.read_multi_line()
            while code != ")":
                self._cache_import(code)
                code = self.read_multi_line()
        else:
            self._cache_import(args[1])

    def run_direct_command(self, text):
        execute_content = self.direct_command(text)
        if execute_content:
            self._write_to_file(self.CACHE_FILE_PATH, execute_content)
            self.execute()

    def process(self, block):
        if block.is_func():
            self.custom_methods.add(block)
        else:
            self.cache_code(block)
            try:
                execute_content = self.prepare()
                self._write_to_file(self.CACHE_FILE_PATH, execute_content)
                return self.execute()
            except NotDeclaredError:
                print("parameter not declared")
                self._rollback()

    def direct_command(self, command):
        return self._template.replace(
            "{%import_area%}", "\"fmt\""
        ).replace(
            "{%func_area%}", ""
        ).replace(
            "{%code_area%}", PRINTLN.format(command)
        )

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

        self.assignment_manager.clear()
        return self._parse_output(out, err)

    def _parse_err_message(self, err):
        error_reason, detail = err.decode("utf8").strip().split("\n")
        return "\n".join(error_reason, detail.split(":")[-1])

    def _rollback(self):
        self.codes.rollback()

    def _parse_output(self, out, err):
        if err:
            self._rollback()
            return self._parse_err_message(err)
        if out:
            return out.decode("utf8").rstrip()

    def cache_code(self, block):
        self.codes.clear()
        self.codes.add(block)

    def _cache_import(self, code):
        package = code.strip(' ,')
        self.packages.add(package)
