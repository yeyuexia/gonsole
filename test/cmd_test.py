# coding: utf8

import unittest
from unittest import mock

from gonsole.cmd import Cmd


class CmdTest(unittest.TestCase):

    @mock.patch('sys.exit')
    def test_invoke_sys_exit_when_given_code_exit(self, mock_exit):
        console = Cmd()

        console._run('exit')

        mock_exit.assert_called_once_with(0)
