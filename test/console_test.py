# coding: utf8

import unittest
from unittest import mock

from libs.console import Console


class TestConsole(unittest.TestCase):

    @mock.patch('sys.exit')
    def test_invoke_sys_exit_when_given_code_exit(self, mock_exit):
        cache = Console('')

        cache.run('exit')

        mock_exit.assert_called_once_with(0)

    def test_cache_import_code_with_single_import(self):
        code = 'import "yyx"'
        cache = Console('')

        cache.run(code)

        self.assertEqual(len(cache.packages), 1)
        self.assertEqual(list(cache.packages.packages)[0], '"yyx"')

    def test_could_not_import_same_package_multi_times(self):
        code = 'import "fmt"'
        cache = Console('')

        cache.run(code)
        cache.run(code)

        self.assertEqual(len(cache.packages), 1)
        self.assertEqual(list(cache.packages.packages)[0], '"fmt"')

    def test_cache_nothing_if_give_empty_str(self):
        cache = Console('')

        cache.run('')

        self.assertEqual(len(cache.codes.codes), 0)


if __name__ == '__main__':
    unittest.main()
