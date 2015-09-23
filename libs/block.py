# coding: utf8

from .const import STANDARD_SPACE


class Block:
    def __init__(self, code):
        self.codes = [code]
        self._get_type()

    def _get_type(self):
        pass

    def append(self, code):
        self.codes.append(code)

    def inflate_space(self, code, indent):
        return STANDARD_SPACE * indent + code

    def get_codes(self):
        for code in self.codes:
            if isinstance(code, Block):
                yield from code.get_codes()
            else:
                yield code

    def deflate(self, indent=0):
        for code in self.codes:
            if isinstance(code, Block):
                yield from code.deflate(indent+1)
            else:
                yield self.inflate_space(code, indent)
