# coding: utf8

import unittest
from unittest import mock

from gonsole.block import Block
from gonsole.block import BlockGenerator


class TestBlockManager(unittest.TestCase):
    def setUp(self):
        self.block_generator = BlockGenerator()

    def test_create_block_when_give_a_simple_code(self):
        block = self.block_generator.generate("a := 222")

        self.assertEqual(block.get_codes(), ["a := 222"])

    @mock.patch("gonsole.block.continue_input")
    def test_create_block_when_give_a_multi_line_code(self, patch_input):
        patch_input.return_value = "i int}"
        block = self.block_generator.generate("type Counter struct {")

        self.assertEqual(
            block.get_codes(), ["type Counter struct {", "i int}"]
        )

    @mock.patch("gonsole.block.continue_input")
    def test_create_block_when_give_a_multi_line_code_with_bracket(
        self, patch_input
    ):
        patch_input.return_value = "i)"
        block = self.block_generator.generate("fmt.Println(")

        self.assertEqual(
            block.get_codes(), ["fmt.Println(", "i)"]
        )


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

    def test_success_judge_is_declared_block_when_use_key_word_type(self):
        block = Block("type Counter int")

        result = block.is_declared()

        self.assertTrue(result)

    def test_success_judge_is_declared_when_declared_multi_varis(self):
        block = Block("x, y := 1, 2")

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

    def test_success_get_vari_when_use_key_word_type(self):
        block = Block("type Counter int")

        varis = set(block.get_declared_varis())
        self.assertTrue("Counter" in varis)
        self.assertEqual(len(varis), 1)


if __name__ == '__main__':
    unittest.main()
