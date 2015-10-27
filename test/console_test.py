# coding: utf8

import unittest
from unittest import mock

from libs.console import Console
from libs.block import Block

from libs.exceptions import NotDeclaredError


class TestConsole(unittest.TestCase):

    @mock.patch('sys.exit')
    def test_invoke_sys_exit_when_given_code_exit(self, mock_exit):
        console = Console('')

        console.parse_input('exit')

        mock_exit.assert_called_once_with(0)

    def test_console_import_code_with_single_import(self):
        code = 'import "yyx"'
        console = Console('')

        console.parse_input(code)

        self.assertEqual(
            len(console.packages.get_declared()), 2
        )
        self.assertTrue(
            "yyx" in console.packages.get_declared()
        )

    def test_could_not_import_same_package_multi_times(self):
        code = 'import "fmt"'
        console = Console('')
        console.packages.assignment_manager.get_all_declared().clear()

        console.parse_input(code)
        console.parse_input(code)

        self.assertEqual(
            len(console.packages.get_declared()), 1
        )
        self.assertTrue(
            "fmt" in console.packages.get_declared()
        )

    def test_console_nothing_if_give_empty_str(self):
        console = Console('')

        console.parse_input('')

        self.assertEqual(len(console.codes.blocks), 0)

    def test_handle_function_when_code_was_start_with_func(self):
        console = Console("")
        console.cache_func = mock.MagicMock()
        code = "func test():"

        console.parse_input(code)

        console.cache_func.assert_called_once_with(code)

    def test_call_export_when_input_export_command(self):
        console = Console("")
        console.export = mock.MagicMock()
        code = "export test"

        console.parse_input(code)

        console.export.assert_called_once_with(code)


class TestConsoleIntegration(unittest.TestCase):

    def test_if_a_variable_not_declared_before_should_raise_error(self):
        console = Console("")
        console.assignment_manager.clear()

        console.codes.add(Block("b = 2"))
        with self.assertRaises(NotDeclaredError):
            console.prepare()

    def test_defined_method_but_not_call_it_should_not_assigned(self):
        console = Console("")
        console.assignment_manager.clear()
        block = Block("func a(i int) {")
        block.append(Block("fmt.Println(i)"))
        block.append(Block("}"))

        console.custom_methods.add(block)
        console.custom_methods.scan_used(console.codes.blocks)
        console.packages.scan_used(
            console.codes.blocks + console.custom_methods.methods
        )

        self.assertEqual(len(console.custom_methods.methods), 0)

    def test_pre_define_vari_a_then_overload_a_as_method_should_change_assignment(self):
        console = Console("")
        console.assignment_manager.clear()
        block = Block("func a(i int) {")
        block.append(Block("fmt.Println(i)"))
        block.append(Block("}"))

        console.codes.add(Block("a := 1"))
        console.custom_methods.add(block)
        console.codes.add(Block("a(2)"))
        console.custom_methods.scan_used(console.codes.blocks)
        console.packages.scan_used(
            console.codes.blocks + console.custom_methods.methods
        )

        self.assertTrue("a" not in console.codes.get_assignments())
        self.assertTrue("a" in console.custom_methods.get_assignments())

    def test_if_invoke_vari_could_get_the_vari_declared(self):
        console = Console("")
        console.assignment_manager.clear()

        console.codes.add(Block("a := 1"))
        console.codes.add(Block('b := "hello"'))
        console.codes.add(Block('c := b + "?"'))
        console.codes.add(Block('a++'))
        self.assertTrue("a" in console.codes.get_assignments())
        self.assertTrue(
            "a" in console.assignment_manager.get_all_assigned()
        )


if __name__ == '__main__':
    unittest.main()
