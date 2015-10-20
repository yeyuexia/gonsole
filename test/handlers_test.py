# coding: utf8
import unittest

from libs import utils

from libs.handlers import CodeHandler
from libs.handlers import PackageHandler
from libs.handlers import FunctionHandler
from libs.block import Block


class TestPackageHandler(unittest.TestCase):
    def test_return_true_when_simple_use_builtin_package(self):
        handler = PackageHandler()
        package = 'fmt'
        code = 'fmt.Println("abc")'

        result = handler.is_assigned(package, code)

        self.assertTrue(result)

    def test_return_true_when_use_third_package(self):
        handler = PackageHandler()
        package = 'com.yyx.console'
        code = "console.Find()"

        result = handler.is_assigned(package, code)

        self.assertTrue(result)

    def test_return_true_when_use_functional_method(self):
        handler = PackageHandler()
        package = 'com.yyx.console'
        code = "console.Find().get()"

        result = handler.is_assigned(package, code)

        self.assertTrue(result)

    def test_scan_used_package_when_block_is_condition_code(self):
        handler = PackageHandler()
        handler.codes = {'com.yyx.console': True}
        block = Block("if a == 1 {")
        block.append(Block("console.Find().get()"))
        block.append("}")

        handler.scan_used([block])

        self.assertEqual(len(handler.assignments), 1)

    def test_should_clear_old_package_when_scan_used_package(self):
        handler = PackageHandler()
        handler.codes = {'com.yyx.console': 1}
        handler.assignments = set(["com.yyx.text"])
        block = Block("if a == 1 {")
        block.append(Block("console.Find().get()"))
        block.append("}")

        handler.scan_used([block])

        self.assertEqual(len(handler.assignments), 1)
        self.assertTrue("com.yyx.text" not in handler.assignments)


class TestFuncHandler(unittest.TestCase):
    def test_success_add_block(self):
        handler = FunctionHandler()
        handler.add(Block("func Str2int(sint string) {"))

        self.assertEqual(len(handler.methods), 1)

    def test_should_get_method_name(self):
        handler = FunctionHandler()
        handler.add(Block("func Str2int(sint string) {"))

        self.assertTrue("Str2int" in handler.codes)

    def test_should_find_used_method(self):
        handler = FunctionHandler()
        handler.codes["Str2int"] = Block("func Str2int(sint string) {")

        code = Block('fmt.Println("test" + Str2int("5"))')
        handler.scan_used([code])

        self.assertTrue("Str2int" in handler.assignments)

    def test_should_clear_old_assignment_when_scan_used_method(self):
        handler = FunctionHandler()
        handler.codes["Str2int"] = Block("func Str2int(sint string) {")
        handler.assignments = set(["aaa"])

        code = Block('fmt.Println("test" + Str2int("5"))')
        handler.scan_used([code])

        self.assertTrue("Str2int" in handler.assignments)
        self.assertTrue("aaa" not in handler.assignments)


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
