# coding: utf8

import unittest
from unittest import mock

from gonsole.console import Console
from gonsole.block import Block

from gonsole.exceptions import NotDeclaredError


class TestConsole(unittest.TestCase):

    @mock.patch('sys.exit')
    def test_invoke_sys_exit_when_given_code_exit(self, mock_exit):
        console = Console()

        console._run('exit')

        mock_exit.assert_called_once_with(0)

    def test_console_import_code_with_single_import(self):
        code = 'import "yyx"'
        console = Console()

        console._run(code)

        self.assertEqual(
            len(console.packages.get_declared()), 2
        )
        self.assertTrue(
            "yyx" in console.packages.get_declared()
        )

    def test_could_not_import_same_package_multi_times(self):
        code = 'import "fmt"'
        console = Console()
        console.packages.assignment_manager.get_all_declared().clear()

        console._run(code)
        console._run(code)

        self.assertEqual(
            len(console.packages.get_declared()), 1
        )
        self.assertTrue(
            "fmt" in console.packages.get_declared()
        )

    def test_handle_function_when_code_was_start_with_func(self):
        console = Console()
        console.custom_methods = mock.MagicMock()
        block = Block("func test()")

        console.process(block)

        console.custom_methods.add.assert_called_once_with(block)

    def test_call_export_when_input_export_command(self):
        console = Console()
        console.do_export = mock.MagicMock()
        code = "export test"

        console._run(code)

        console.do_export.assert_called_once_with("test")

    def test_give_a_direct_command_would_invoke_direct_method(self):
        console = Console()
        console.direct_command = mock.MagicMock()
        console._write_to_file = mock.MagicMock()
        console.execute = mock.MagicMock()
        code = "12 + 34"

        console.try_run_direct_command(code)

        console.direct_command.assert_called_once_with(code)


class TestConsoleIntegration(unittest.TestCase):

    def test_if_a_variable_not_declared_before_should_raise_error(self):
        console = Console()
        console.assignment_manager.clear()

        console.codes.add(Block("b = 2"))
        with self.assertRaises(NotDeclaredError):
            console.prepare()

    def test_defined_method_but_not_call_it_should_not_assigned(self):
        console = Console()
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
        console = Console()
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

        self.assertTrue("a" not in console.codes.get_params())
        self.assertTrue("a" in console.custom_methods.get_params())

    def test_if_invoke_vari_could_get_the_vari_declared(self):
        console = Console()
        console.assignment_manager.clear()

        console.codes.add(Block("a := 1"))
        console.codes.add(Block('b := "hello"'))
        console.codes.add(Block('c := b + "?"'))
        console.codes.add(Block('a++'))
        self.assertTrue("a" in console.codes.get_params())
        self.assertTrue(
            "a" in console.assignment_manager.get_all_assigned()
        )


if __name__ == '__main__':
    unittest.main()
