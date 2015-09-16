# coding: utf8

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

    CODE_TEMPLATE = "{%code_area%}"

    def __init__(self):
        self.codes = list()

    def add(self, code):
        self.codes.append(code)

    def inflate(self, template):
        return template.replace(self.CODE_TEMPLATE, self._parse_code())

    def _parse_code(self):
        return "\n".join(self.codes)
