# coding: utf8
import re

from . import utils


class PackageHandler:

    IMPORT_TEMPLATE = "{%import_area%}"

    def __init__(self):
        self.packages = set()
        self.used_packages = set()

        self._add_default_packages()

    def _add_default_packages(self):
        self.packages.add('fmt')

    def add(self, package):
        self.packages.add(package.strip('"'))

    def __len__(self):
        return len(self.packages)

    def used_package_length(self):
        return len(self.used_packages)

    def inflate(self, template):
        return template.replace(self.IMPORT_TEMPLATE, self._parse_packages())

    def scan_used_package(self, block):
        for _code in utils.parse_block(block):
            self.used_packages.update(
                package for package in self.packages if self._used_package(
                    package, _code
                )
            )

    def _used_package(self, package, code):
        package = package.split('.')[-1]
        return code.find(package) == 0

    def _parse_packages(self):
        return "\n".join(
            self._format(package) for package in self.used_packages
        )

    def _format(self, package):
        return utils.STANDARD_SPACE + '"' + package + '"'


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
        self.blocks = dict()
        self.auto_increment = 0
        self.varis = dict()
        self.assignments = dict()

    def _get_and_increment_index(self):
        index = self.auto_increment
        self.auto_increment += 1

        return index

    def add(self, block):
        index = self._get_and_increment_index()
        self.blocks[index] = block

        if self.is_assignment_block(block):
            self._store_assignments(index, block)
        else:
            self._scan_used_assignments(index, block)

    def rollback(self):
        index = max(self.blocks)
        self._remove_assignment(index)
        del self.blocks[index]

    def _remove_assignment(self, index):
        [v.remove(index) for k, v in self.assignments.items() if index in v]

    def _store_assignments(self, index, block):
        varis = self._get_varis(block)

        self.varis.update([(vari, index) for vari in varis])
        self.assignments.update([(vari, []) for vari in varis])

    def _get_varis(self, block):
        return [
            _code.split('=')[0].strip(" :")
            for _code in utils.parse_block(block)
            if self._is_assignment(_code)
        ]

    def _scan_used_assignments(self, index, block):
        for _code in utils.parse_block(block):
            [
                self.assignments[vari].append(index)
                for vari in self.assignments
                if self._used_assignment(vari, _code)
            ]

    def _used_assignment(self, vari, code):
        return code.find(vari) == 0

    def inflate(self, template):
        return template.replace(self.CODE_TEMPLATE, self._parse_code())

    def is_assignment_block(self, block):
        for code in block.get_codes():
            if self._is_assignment(code):
                return True
        return False

    def _is_assignment(self, code):
        return self.IS_ASSIGNMENT_RE.match(code)

    def _deflate_blocks(self):
        for index, block in self.blocks.items():
            if self._need_compile(index):
                yield from block.deflate()

    def _parse_code(self):
        return "\n".join(list(self._deflate_blocks()))

    def _need_compile(self, index):
        if index not in self.varis.values():
            return True
        for vari, _index in self.varis.items():
            if _index == index and len(self.assignments[vari]) > 0:
                return True
        return False
