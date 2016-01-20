# coding: utf8

import re
import threading

from . import utils


class AssignmentManager:

    _instance = None

    _lock = threading.Lock()

    def __init__(self):
        self.assigned_params = dict()
        self.declared_params = dict()

    @classmethod
    def instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = AssignmentManager()
        return cls._instance

    def add_assigned(self, param, param_type):
        self.assigned_params[param] = param_type

    def add_declared(self, handler_type, name, codes):
        self.declared_params[name] = (handler_type, codes)

    def get_assigned(self, handler_type):
        for assignment, _type in self.assigned_params.items():
            if _type == handler_type:
                yield assignment

    def get_all_assigned(self):
        return self.assigned_params.keys()

    def get_all_declared(self):
        return self.declared_params

    def get_declared(self, assignment_type):
        declareds = dict()
        for name, value in self.declared_params.items():
            if value[0] == assignment_type:
                declareds[name] = value[1]
        return declareds

    def clear(self):
        self.assigned_params.clear()

    def length(self):
        return len(self.assigned_params)


class Handler(object):  # for compatibility to python 2.x

    def __init__(self, template, handler_type):
        self.handler_type = handler_type
        self.template = template
        self.assignment_manager = AssignmentManager.instance()

    def scan(self, block):
        for code in block.parse_to_codes():
            for name in self.get_declared():
                if self.is_assigned(name, code):
                    self.assignment_manager.add_assigned(
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

    def get_params(self):
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
            for name in self.get_params()
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
        return [self.get_declared()[name] for name in self.get_params()]

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
            if name in self.get_params():
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
            if not used_varis:
                return
            for vari in used_varis:
                scanned_varis.add(vari)
                self.scan(self.get_declared()[vari])

            scan_used_codes(set(self.get_params()) - scanned_varis)

        self.scan(self._pre_executed)
        scan_used_codes(set(self.get_params()))
        self._execute_blocks = self._generate_execute_blocks()

    def get_last(self):
        return self._pre_executed

    def add(self, block):
        self._blocks.append(block)
        self._pre_executed = block

        def add_declareds(block):
            [self.add_declared(vari, block)
                for vari in block.get_declared_varis()]

        add_declareds(block) if block.is_declared() else self._scan_for_execute()

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
        return [
            block for block in self._blocks if self.need_compile(block)
        ]

    def _deflate_block(self, blocks):
        _blocks = list()
        for block in blocks:
            _blocks.extend(block.deflate(1))
        return _blocks

    def parse_codes(self):
        return "\n".join(list(self._deflate_block(self.blocks)))

    def get_propable_params(self, block):
        for param in self.get_params():
            index = self._blocks.index(self.get_declared()[param])
            if index <= self._blocks.index(block):
                yield param

    def need_compile(self, block):
        if block == self._pre_executed:
            return True

        params = list(self.get_propable_params(block))

        def check_has_assigned_vari(code):
            return any([
                self.is_assigned(param, code)
                for param in params
            ])
        return any([
            check_has_assigned_vari(code)
            for code in block.parse_to_codes()
        ])
