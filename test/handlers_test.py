# coding: utf8
import unittest

from handlers import PackageHandler


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


if __name__ == '__main__':
    unittest.main()
