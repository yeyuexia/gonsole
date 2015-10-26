# coding: utf8

import unittest
from unittest import mock

from libs.console import Console
from libs.block import Block


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

        self.assertEqual(len(console.packages), 2)
        self.assertTrue("yyx" in console.packages.declared_assignments)

    def test_could_not_import_same_package_multi_times(self):
        code = 'import "fmt"'
        console = Console('')

        console.parse_input(code)
        console.parse_input(code)

        self.assertEqual(len(console.packages.declared_assignments), 1)
        self.assertTrue("fmt" in console.packages.declared_assignments)

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

    def test_parse_single_code(self):
        console = Console('')

        result = console.parse_block(Block('fmt.Println("aa")'))

        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 1)

    def test_parse_two_method_when_use_package_method_as_anothers_value(self):
        console = Console('')
        block = Block("get(console.Find())")

        result = console.parse_block(block)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].startswith('get'), True)
        self.assertEqual(result[1].startswith('console.'), True)

    def test_parse_one_metho_when_a_string_like_method(self):
        console = Console('')
        block = Block('get("console.Find()")')

        result = console.parse_block(block)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].startswith('get'), True)

    def test_call_export_when_input_export_command(self):
        console = Console("")
        console.export = mock.MagicMock()
        code = "export test"

        console.parse_input(code)

        console.export.assert_called_once_with(code)


class TestConsoleIntegration(unittest.TestCase):

    def test_defined_method_but_not_call_it_should_not_assigned(self):
        console = Console("")
        block = Block("func a(i int) {")
        block.append(Block("fmt.Println(i)"))
        block.append(Block("}"))
        console.custom_methods.add(block)

        console.custom_methods.scan_used(console.codes.blocks)
        console.packages.scan_used(
            console.codes.blocks + console.custom_methods.methods
        )

        self.assertEqual(len(console.custom_methods.methods), 0)

if __name__ == '__main__':
    unittest.main()
