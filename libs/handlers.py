# coding: utf8
import re

from . import utils


class PackageHandler:

    IMPORT_TEMPLATE = "{%import_area%}"

    def __init__(self):
        self.packages = set()
        self.used_packages = set()

    def add(self, package):
        self.packages.add(package)

    def __len__(self):
        return len(self.packages)

    def used_package_length(self):
        return len(self.used_packages)

    def inflate(self, template):
        return template.replace(self.IMPORT_TEMPLATE, self._parse_packages())

    def scan_used_package(self, code):
        for _code in utils.parse_code(code):
            self.used_packages.update(
                package for package in self.packages if self._used_package(
                    package, _code
                )
            )

    def _used_package(self, package, code):
        package = package.strip('"').split('.')[-1]
        return code.find(package) == 0

    def _parse_packages(self):
        return "\n".join(
            self._format(package) for package in self.used_packages
        )

    def _format(self, package):
        return utils.STANDARD_SPACE + package


class FunctionHandler:

    FUNC_TEMPLATE = "{%func_area%}"

    def __init__(self):
        self.funcs = list()

    def add(self, func):
        self.funcs.append(func)

    def inflate(self, template):
        return template.replace(self.FUNC_TEMPLATE, self._parse_func())

    def _parse_func(self):
        return "\n".join(["\n" + func for func in self.funcs])


class CodeHandler:

    CODE_TEMPLATE = '{%code_area%}'

    IS_ASSIGNMENT_RE = re.compile('.*(\w|:| )=(^=)*')

    def __init__(self):
        self.codes = list()
        self.unused_assignments = dict()

    def add(self, code):
        self.codes.append(code)
        if self.is_assignment(code):
            self.unused_assignments.update(
                self._get_varis(code, self.codes.index(code))
            )
        self._check_use_assignment(code)

    def _get_varis(self, code, index):
        return [(_code.split('=').strip(), index) for
                _code in utils.parse_code(code) if self.is_assignment(_code)]

    def _check_use_assignment(self, code):
        for _code in utils.parse_code(code):
            used_vars = [
                vari for vari in self.unused_assignments if
                self._used_assignment(vari, _code)
            ]
            utils.batch_remove(self.used_assignments, used_vars)

    def _used_assignment(self, vari, code):
        return code.find(vari) == 0

    def inflate(self, template):
        return template.replace(self.CODE_TEMPLATE, self._parse_code())

    def is_assignment(self, code):
        return self.IS_ASSIGNMENT_RE.match(code)

    def _parse_code(self):
        return "\n".join(
            [code for code in self.codes if
                self.codes.index(code) not in
                self.unused_assignments.values()]
        )
