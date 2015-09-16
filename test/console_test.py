# coding: utf8

import unittest
from unittest import mock

from libs.console import GoCodeCache


class TestGoCodeCache(unittest.TestCase):

    @mock.patch('sys.exit')
    def test_invoke_sys_exit_when_given_code_exit(self, mock_exit):
        cache = GoCodeCache('')

        cache.run('exit')

        mock_exit.assert_called_once_with(0)

    def test_cache_import_code_with_single_import(self):
        code = 'import "yyx"'
        cache = GoCodeCache('')

        cache.run(code)

        self.assertEqual(len(cache.packages), 1)
        self.assertEqual(list(cache.packages.packages)[0], '"yyx"')

    def test_could_not_import_same_package_multi_times(self):
        code = 'import "fmt"'
        cache = GoCodeCache('')

        cache.run(code)
        cache.run(code)

        self.assertEqual(len(cache.packages), 1)
        self.assertEqual(list(cache.packages.packages)[0], '"fmt"')

    def test_cache_nothing_if_give_empty_str(self):
        cache = GoCodeCache('')

        cache.run('')

        self.assertEqual(len(cache.codes.codes), 0)


if __name__ == '__main__':
    unittest.main()
