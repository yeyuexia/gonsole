# coding: utf8

import unittest
from unittest import mock

from libs.console import Console
from libs.block import Block


class TestConsole(unittest.TestCase):

    @mock.patch('sys.exit')
    def test_invoke_sys_exit_when_given_code_exit(self, mock_exit):
        console = Console('')

        console._parse_input('exit')

        mock_exit.assert_called_once_with(0)

    def test_console_import_code_with_single_import(self):
        code = 'import "yyx"'
        console = Console('')

        console._parse_input(code)

        self.assertEqual(len(console.packages), 2)
        self.assertEqual(list(console.packages.packages)[1], 'yyx')

    def test_could_not_import_same_package_multi_times(self):
        code = 'import "fmt"'
        console = Console('')

        console._parse_input(code)
        console._parse_input(code)

        self.assertEqual(len(console.packages), 1)
        self.assertEqual(list(console.packages.packages)[0], 'fmt')

    def test_console_nothing_if_give_empty_str(self):
        console = Console('')

        console._parse_input('')

        self.assertEqual(len(console.codes.blocks), 0)

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


if __name__ == '__main__':
    unittest.main()


if __name__ == '__main__':
    unittest.main()
