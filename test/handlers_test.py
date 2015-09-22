# coding: utf8
import unittest

from libs.handlers import PackageHandler
from libs.handlers import CodeHandler
from libs.block import Block


class TestPackageHandler(unittest.TestCase):
    def test_return_true_when_simple_use_builtin_package(self):
        handler = PackageHandler()
        package = '"fmt"'
        code = 'fmt.Println("abc")'

        result = handler._used_package(package, code)

        self.assertEqual(result, True)

    def test_return_true_when_use_third_package(self):
        handler = PackageHandler()
        package = '"com.yyx.console"'
        code = "console.Find()"

        result = handler._used_package(package, code)

        self.assertEqual(result, True)

    def test_return_true_when_use_functional_method(self):
        handler = PackageHandler()
        package = '"com.yyx.console"'
        code = "console.Find().get()"

        result = handler._used_package(package, code)

        self.assertEqual(result, True)


class TestCodeHandler(unittest.TestCase):
    def test_success_check_is_assignment(self):
        code = 'a := "123"'
        handler = CodeHandler()

        result = handler._is_assignment(code)

        self.assertEqual(result and True, True)

    def test_check_is_not_assignment(self):
        code = '1 <= 2'
        handler = CodeHandler()

        result = handler._is_assignment(code)

        self.assertEqual(result or False, False)

    def test_can_check_used_assignment(self):
        handler = CodeHandler()
        handler.varis = dict(a=0)
        handler.assignments = dict(a=[])

        block = Block('fmt.Println(a)')
        handler._scan_used_assignments(1, block)

        self.assertEqual(len(handler.assignments["a"]), 1)
        self.assertEqual(handler.assignments["a"], [1])

    def test_is_need_compile_would_return_true_if_not_assignment_code(self):
        handler = CodeHandler()

        result = handler._need_compile(1)

        self.assertEqual(result, True)

    def test_is_used_assignment_need_compile_would_return_true(self):
        handler = CodeHandler()
        handler.varis = dict(a=1)
        handler.assignments = dict(a=[2])

        result = handler._need_compile(1)

        self.assertEqual(result, True)


if __name__ == '__main__':
    unittest.main()
