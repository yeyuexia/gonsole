# coding: utf8

import sys
import subprocess

from handlers import PackageHandler

STANDARD_SPACE = "    "


def single_line_input():
    return input(">").strip()


def inflate_space(code):
    return STANDARD_SPACE+code


def continue_input():
    return input(STANDARD_SPACE).strip()


class GoCodeCache:
    GO_CODE_TEMPLATE = "go_template"
    CODE_TEMPLATE = "{%code_area%}"
    FUNC_TEMPLATE = "{%func_area%}"
    CACHE_FILE_PATH = "console/_cache/main.go"

    def __init__(self):
        with open(self.GO_CODE_TEMPLATE) as f:
            self._template = f.read()
        self.codes = []
        self.packages = PackageHandler()
        self.custom_funcs = []

    def run(self, command):
        if command == "exit":
            sys.exit(0)
        elif command.startswith("import "):
            self.cache_packages(command)
        elif command.startswith("func "):
            self.cache_func(command)
        else:
            self.cache_code(command)
            self.execute()

    def inflate_func(self, template=None):
        template = template or self._template
        return template.replace(self.FUNC_TEMPLATE, self._parse_func())

    def inflate_code(self, template=None):
        template = template or self._template
        return template.replace(self.CODE_TEMPLATE, self._parse_code())

    def _parse_func(self):
        return "\n".join(["\n" + func for func in self.custom_funcs])

    def _parse_code(self):
        return "\n".join(self.codes)

    def execute(self):
        with open(self.CACHE_FILE_PATH, "w") as f:
            f.write(self.packages.inflate(
                self.inflate_func(self.inflate_code())
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
        self.codes.append(code)

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


def run_console():
    cache = GoCodeCache()
    while True:
        cache.run(single_line_input())


if __name__ == "__main__":
    run_console()
