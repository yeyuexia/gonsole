# coding: utf8

import re
import threading

from . import utils


class AssignmentManager:

    _instance = None

    _lock = threading.Lock()

    def __init__(self):
        self.assignments = dict()
        self.declared_assignments = dict()

    @classmethod
    def instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = AssignmentManager()
        return cls._instance

    def add_assignment(self, assignment, assignment_type):
        self.assignments[assignment] = assignment_type

    def add_declared(self, assignment_type, assignment, codes):
        self.declared_assignments[assignment] = (assignment_type, codes)

    def get_assigned(self, assignment_type):
        for assignment, _type in self.assignments.items():
            if _type == assignment_type:
                yield assignment

    def get_all_assigned(self):
        return self.assignments.keys()

    def get_all_declared(self):
        return self.declared_assignments

    def get_declared(self, assignment_type):
        declareds = dict()
        for name, value in self.declared_assignments.items():
            if value[0] == assignment_type:
                declareds[name] = value[1]
        return declareds

    def clear(self):
        self.assignments.clear()

    def length(self):
        return len(self.assignments)


class Handler(object):  # for compatibility to python 2.x

    def __init__(self, template, handler_type):
        self.handler_type = handler_type
        self.template = template
        self.assignment_manager = AssignmentManager.instance()

    def scan(self, block):
        for code in block.parse_to_codes():
            for name in self.get_declared():
                if self.is_assigned(name, code):
                    self.assignment_manager.add_assignment(
                        name, self.handler_type
                    )

    def add(self, codes):
        raise NotImplementedError()

    def scan_used(self, blocks):
        for block in blocks:
            self.scan(block)

    def is_assigned(self, name, code):
        raise NotImplementedError()

    def parse_codes(self):
        raise NotImplementedError()

    def inflate(self, template):
        return template.replace(self.template, self.parse_codes())

    def get_assignments(self):
        return self.assignment_manager.get_assigned(self.handler_type)

    def add_declared(self, name, codes):
        self.assignment_manager.add_declared(self.handler_type, name, codes)

    def get_declared(self):
        return self.assignment_manager.get_declared(self.handler_type)


class PackageHandler(Handler):

    IMPORT_TEMPLATE = "{%import_area%}"

    def __init__(self):
        super(PackageHandler, self).__init__(self.IMPORT_TEMPLATE, "package")

        self._add_default_packages()

    def _add_default_packages(self):
        self.add('fmt')

    def add(self, package):
        package = package.strip('"')
        self.add_declared(package, package)

    def used_package_length(self):
        return self.assignment_manager.length()

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
        return [self.get_declared()[name] for name in self.get_assignments()]

    def add(self, method):
        method_name = self._get_method_name(method)
        self.add_declared(method_name, method)

    def _get_method_name(self, method):
        return self.METHOD_NAME_RE.search(method.codes[0]).group("method_name")

    def parse_codes(self):
        return "\n\n".join(list(self._assemble()))

    def _assemble_method(self, method):
        return "\n".join(list(method.deflate()))

    def _assemble(self):
        for name, method in self.get_declared().items():
            if name in self.get_assignments():
                yield self._assemble_method(method)

    def is_assigned(self, method, code):
        return code.find(method) == 0


class CodeHandler(Handler):

    CODE_TEMPLATE = "{%code_area%}"

    IS_ASSIGNMENT_RE = re.compile(r"(?P<vari>\w+)[ ]*:=[^=]+")
    VARIABLE_DECLARE_RE = re.compile("(var|const) (?P<vari>\w+) ")

    def __init__(self):
        super(CodeHandler, self).__init__(self.CODE_TEMPLATE, "code")
        self._pre_executed = None
        self._blocks = list()
        self._execute_blocks = list()

    @property
    def blocks(self):
        return self._execute_blocks

    def _scan_for_execute(self):
        scanned_varis = set()

        def scan_used_codes(used_varis):
            scanned_varis.update(used_varis)
            for varis in used_varis:
                self.scan(self.get_declared()[varis])
            used_names = set(self.get_assignments())
            if scanned_varis != used_names:
                scan_used_codes(used_names - scanned_varis)

        self.scan(self._pre_executed)
        scan_used_codes(set(self.get_assignments()))
        self._generate_execute_blocks()

    def get_last(self):
        return self._pre_executed

    def add(self, block):
        self._blocks.append(block)
        self._pre_executed = block

        if not block.is_declared():
            self._scan_for_execute()
        else:
            for vari in block.get_declared_varis():
                self.add_declared(vari, block)

    def rollback(self):
        self._blocks.pop()

    def clear(self):
        self._pre_executed = None
        self._execute_blocks = list()

    def get_varis(self, block):
        return set(block.get_declared_varis())

    def is_assigned(self, vari, code):
        return code.find(vari) == 0

    def _generate_execute_blocks(self):
        self._execute_blocks = [
            block for block in self._blocks if self.need_compile(block)
        ]

    def _deflate_block(self, blocks):
        _blocks = list()
        for block in blocks:
            _blocks.extend(block.deflate(1))
        return _blocks

    def parse_codes(self):
        return "\n".join(list(self._deflate_block(self.blocks)))

    def need_compile(self, block):
        if block == self._pre_executed:
            return True
        varis = list(self.get_assignments())
        for code in block.parse_to_codes():
            for vari in varis:
                if self.is_assigned(vari, code):
                    return True
        return False
