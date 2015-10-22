# coding: utf8

import re
import threading

from . import utils


class AssignmentHandler:

    _instance = None

    _lock = threading.Lock()

    def __init__(self):
        self.assignments = dict()

    @classmethod
    def instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = AssignmentHandler()
        return cls._instance

    def add(self, assignment, assignment_type):
        self.assignments[assignment] = assignment_type

    def get(self, assignment_type):
        for assignment, _type in self.assignments.items():
            if _type == assignment_type:
                yield assignment

    def clear(self):
        self.assignments.clear()

    def length(self):
        return len(self.assignments)


class Handler:

    def __init__(self, template, handler_type):
        self.handler_type = handler_type
        self.template = template
        self.assignments = AssignmentHandler.instance()
        self.codes = dict()

    def scan(self, block):
        for code in utils.parse_block(block):
            for name in self.codes:
                if self.is_assigned(name, code):
                    self.assignments.add(name, self.handler_type)

    def add(self, codes):
        raise NotImplementedError()

    def scan_used(self, blocks):
        self.assignments.clear()
        for block in blocks:
            self.scan(block)

    def is_assigned(self, name, code):
        raise NotImplementedError()

    def parse_codes(self):
        raise NotImplementedError()

    def inflate(self, template):
        return template.replace(self.template, self.parse_codes())

    def get_assignments(self):
        return self.assignments.get(self.handler_type)


class PackageHandler(Handler):

    IMPORT_TEMPLATE = "{%import_area%}"

    def __init__(self):
        super(PackageHandler, self).__init__(self.IMPORT_TEMPLATE, "package")

        self._add_default_packages()

    def _add_default_packages(self):
        self.add('fmt')

    def add(self, package):
        self.codes[(package.strip('"'))] = True

    def __len__(self):
        return len(self.codes)

    def used_package_length(self):
        return self.assignments.length()

    def is_assigned(self, name, code):
        name = name.split('.')[-1]
        return code.find(name) == 0

    def parse_codes(self):
        return "\n".join(
            self._format(name)
            for name in self.get_assignments()
        )

    def _format(self, package):
        return utils.STANDARD_SPACE + '"' + package + '"'


class FunctionHandler(Handler):

    FUNC_TEMPLATE = "{%func_area%}"
    METHOD_NAME_RE = re.compile("func (?P<method_name>\w+)\(")

    def __init__(self):
        super(FunctionHandler, self).__init__(self.FUNC_TEMPLATE, "method")

    @property
    def methods(self):
        return list(self.codes.values())

    def add(self, method):
        method_name = self._get_method_name(method)
        self.codes[method_name] = method
        self.scan(method)

    def _get_method_name(self, method):
        return self.METHOD_NAME_RE.search(method.codes[0]).group("method_name")

    def parse_codes(self):
        return "\n\n".join(list(self._assemble()))

    def _assemble_method(self, method):
        return "\n".join(list(method.deflate()))

    def _assemble(self):
        for name, method in self.codes.items():
            if name in self.get_assignments():
                yield self._assemble_method(method)

    def is_assigned(self, method, code):
        return code.find(method) == 0


class CodeHandler:

    CODE_TEMPLATE = "{%code_area%}"

    IS_ASSIGNMENT_RE = re.compile(r"(?P<vari>\w+)[ ]*:=[^=]+")
    VARIABLE_DECLARE_RE = re.compile("(var|const) (?P<vari>\w+) ")

    def __init__(self):
        self._blocks = dict()
        self.auto_increment = 0
        self.varis = dict()
        self.assignments = dict()

    @property
    def blocks(self):
        return [
            block
            for index, block in self._blocks.items()
            if self._need_compile(index)
        ]

    def _get_and_increment_index(self):
        index = self.auto_increment
        self.auto_increment += 1

        return index

    def add(self, block):
        index = self._get_and_increment_index()
        self._blocks[index] = block

        if self.is_assignment_block(block):
            self._store_assignments(index, block)
        else:
            self._scan_used_assignments(index, block)

    def rollback(self):
        index = max(self._blocks)
        self._remove_assignment(index)
        del self._blocks[index]

    def _remove_assignment(self, index):
        [v.remove(index) for k, v in self.assignments.items() if index in v]

    def _store_assignments(self, index, block):
        varis = self.get_varis(block)
        self.varis.update([(vari, index) for vari in varis])

        self.assignments.update([(vari, []) for vari in varis])

    def get_varis(self, block):
        return set(self._get_varis(block))

    def _get_varis(self, block):
        for code in utils.parse_block(block):
            result = self._is_assignment(code)
            if result:
                yield result.group("vari")

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
        return self.VARIABLE_DECLARE_RE.match(code) or self.IS_ASSIGNMENT_RE.match(code)

    def _deflate_blocks(self):
        for index, block in self._blocks.items():
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
