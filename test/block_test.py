# coding: utf8

import unittest

from libs.block import Block


class TestBlock(unittest.TestCase):
    def test_parse_single_code(self):
        block = Block('fmt.Println("aa")')

        result = block.parse_to_codes()

        self.assertEqual(type(result), list)
        self.assertEqual(len(result), 2)

    def test_parse_two_method_when_use_package_method_as_anothers_value(self):
        block = Block("get(console.Find())")

        result = block.parse_to_codes()

        self.assertEqual(len(result), 3)
        self.assertTrue(result[0] == "get(console.Find())")
        self.assertTrue(result[1].startswith("get"))
        self.assertTrue(result[2].startswith('console.'))

    def test_parse_one_metho_when_a_string_like_method(self):
        block = Block('get("console.Find()")')

        result = block.parse_to_codes()

        self.assertEqual(len(result), 2)
        self.assertTrue(result[0].startswith('get'))

    def test_return_true_when_is_a_declared_vari_code(self):
        block = Block("a := 1")

        result = block.is_declared()

        self.assertTrue(result)

    def test_return_false_when_declared_and_used_block(self):
        block = Block("a := 1; a++")

        result = block.is_declared()

        self.assertTrue(not result)

    def test_return_false_when_give_a_not_declared_code(self):
        block = Block("a >= 1")

        result = block.is_declared()

        self.assertTrue(not result)

    def test_success_get_assignment_use_key_word_var(self):
        block = Block("var a int64")

        result = block.is_declared()

        self.assertTrue(result)

    def test_success_get_assignment_use_key_word_const(self):
        block = Block('const x string = "hello world"')

        result = block.is_declared()

        self.assertTrue(result)

    def test_success_judge_is_declared_block(self):
        block = Block('const x string = "hello world"')

        result = block.is_declared()

        self.assertTrue(result)

    def test_success_get_vari_when_use_key_word_var(self):
        block = Block("var a int64")

        varis = set(block.get_declared_varis())

        self.assertTrue("a" in varis)
        self.assertTrue(len(varis) == 1)

    def test_success_get_vari_when_use_key_word_const(self):
        block = Block('const x string = "hello world"')

        varis = set(block.get_declared_varis())

        self.assertTrue("x" in varis)
        self.assertTrue(len(varis) == 1)

    def test_success_get_vari_when_declear(self):
        block = Block('a := "123"')

        varis = set(block.get_declared_varis())

        self.assertTrue("a" in varis)
        self.assertTrue(len(varis) == 1)

if __name__ == '__main__':
    unittest.main()
