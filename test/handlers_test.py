# coding: utf8
import unittest

from libs.handlers import PackageHandler
from libs.handlers import CodeHandler


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

        result = handler.is_assignment(code)

        self.assertEqual(result and True, True)

    def test_check_is_not_assignment(self):
        code = '1 <= 2'
        handler = CodeHandler()

        result = handler.is_assignment(code)

        self.assertEqual(result or False, False)

    def test_can_check_used_assignment(self):
        handler = CodeHandler()
        handler.unused_assignments = dict(a=1)

        handler._check_use_assignment("fmt.Println(a)")

        self.assertEqual(len(handler.unused_assignments), 0)




if __name__ == '__main__':
    unittest.main()
