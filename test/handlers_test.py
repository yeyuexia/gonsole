# coding: utf8
import unittest

from gonsole.block import Block
from gonsole.handlers import CodeHandler
from gonsole.handlers import PackageHandler
from gonsole.handlers import FunctionHandler
from gonsole.handlers import AssignmentManager


class TestAssignmentManager(unittest.TestCase):
    def setUp(self):
        self.handler = AssignmentManager.instance()

    def test_should_add_assigned(self):
        self.handler.assigned_params = dict()

        self.handler.add_assigned("x", "aa")

        self.assertEquals(len(self.handler.assigned_params), 1)
        self.assertTrue("x" in self.handler.assigned_params)
        self.assertEquals(self.handler.assigned_params["x"], "aa")

    def test_should_override_assignment_when_has_same_name(self):
        self.handler.assigned_params = dict()
        self.handler.assigned_params["x"] = "aa"

        self.handler.add_assigned("x", "bb")

        self.assertEquals(len(self.handler.assigned_params), 1)
        self.assertTrue("x" in self.handler.assigned_params)
        self.assertEquals(self.handler.assigned_params["x"], "bb")


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
        handler.add_declared("com.yyx.console", "com.yyx.console")
        block = Block("if a == 1 {")
        block.append(Block("console.Find().get()"))
        block.append("}")

        handler.scan_used([block])
        self.assertEqual(len(list(handler.get_params())), 1)

    def test_should_clear_old_package_when_clear_and_scan_used_package(self):
        handler = PackageHandler()
        handler.add_declared("com.yyx.console", "com.yyx.console")
        handler.assignment_manager.add_assigned(
            "com.yyx.text", handler.handler_type
        )
        block = Block("if a == 1 {")
        block.append(Block("console.Find().get()"))
        block.append("}")

        handler.assignment_manager.clear()

        handler.scan_used([block])

        self.assertEqual(handler.assignment_manager.length(), 1)
        self.assertTrue(
            "com.yyx.text" not in handler.get_params()
        )


class TestFuncHandler(unittest.TestCase):
    def test_success_add_block(self):
        handler = FunctionHandler()
        handler.get_declared().clear()
        handler.add(Block("func Str2int(sint string) {"))

        self.assertEqual(len(handler.get_declared()), 1)

    def test_should_get_method_name(self):
        handler = FunctionHandler()
        handler.get_declared().clear()
        handler.add(Block("func Str2int(sint string) {"))

        self.assertTrue("Str2int" in handler.get_declared())

    def test_should_find_used_method(self):
        handler = FunctionHandler()
        handler.add_declared("Str2int", Block("func Str2int(sint string) {"))

        code = Block('fmt.Println("test" + Str2int("5"))')
        handler.scan_used([code])

        self.assertTrue(
            "Str2int" in handler.get_params()
        )

    def test_should_clear_old_assignment_when_clear(self):
        handler = FunctionHandler()
        handler.add_declared("Str2int", Block("func Str2int(sint string) {"))
        handler.assignment_manager.add_assigned("aaa", handler.handler_type)
        handler.assignment_manager.clear()

        code = Block('fmt.Println("test" + Str2int("5"))')
        handler.scan_used([code])

        self.assertTrue("Str2int" in handler.get_params())
        self.assertTrue("aaa" not in handler.get_params())


class TestCodeHandler(unittest.TestCase):

    def test_could_success_get_last_input_codes(self):
        block = Block("var a int64")
        handler = CodeHandler()

        handler.add(block)

        self.assertEquals(handler.get_last(), block)

    def test_success_get_vari_when_use_key_word_var(self):
        block = Block("var a int64")
        handler = CodeHandler()

        varis = handler.get_varis(block)

        self.assertTrue("a" in varis)
        self.assertTrue(len(varis) == 1)

    def test_success_get_vari_when_use_key_word_const(self):
        block = Block('const x string = "hello world"')
        handler = CodeHandler()

        varis = handler.get_varis(block)

        self.assertTrue("x" in varis)
        self.assertTrue(len(varis) == 1)

    def test_can_check_used_assignment(self):
        handler = CodeHandler()
        handler.varis = dict(a=0)
        handler.get_declared().clear()
        handler.add_declared("a", Block("a := 1"))

        block = Block('fmt.Println(a)')
        handler.scan_used([block])

        self.assertEqual(len(list(handler.get_params())), 1)
        self.assertTrue("a" in handler.get_params())

    def test_is_need_compile_would_return_true_if_not_assignment_code(self):
        handler = CodeHandler()

        declared_block = Block("var a string")
        block = Block("fmt.Println(a)")

        handler._blocks.append(declared_block)
        handler._blocks.append(block)
        handler.add_declared("a", declared_block)
        handler.assignment_manager.add_assigned("a", handler.handler_type)

        result = handler.need_compile(block)

        self.assertTrue(result)

    def test_is_used_assignment_need_compile_would_return_true(self):
        handler = CodeHandler()

        declared_block = Block("a := 1")
        block = Block("a.get()")

        handler._blocks.append(declared_block)
        handler._blocks.append(block)
        handler.add_declared("a", declared_block)

        result = handler.need_compile(block)

        self.assertTrue(result)

    def test_parse_right_codes_when_give_a_simple_block(self):
        handler = CodeHandler()
        handler._execute_blocks = [Block("fmt.Println('1')")]

        codes = handler.parse_codes()

        self.assertEquals("    fmt.Println('1')", codes)


if __name__ == '__main__':
    unittest.main()
