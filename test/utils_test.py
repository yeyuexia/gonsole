# coding: utf8

import unittest

from libs.block import Block
from libs.utils import parse_block


class TestUtils(unittest.TestCase):
    def test_parse_single_code(self):
        result = parse_block(Block('fmt.Println("aa")'))

        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 1)

    def test_parse_two_method_when_use_package_method_as_anothers_value(self):
        block = Block("get(console.Find())")

        result = parse_block(block)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].startswith('get'), True)
        self.assertEqual(result[1].startswith('console.'), True)

    def test_parse_one_metho_when_a_string_like_method(self):
        block = Block('get("console.Find()")')

        result = parse_block(block)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].startswith('get'), True)


if __name__ == '__main__':
    unittest.main()
