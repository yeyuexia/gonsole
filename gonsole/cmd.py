# coding: utf8

import re
import sys
import readline  # import readline to fix console bug

from .const import STANDARD_SPACE
from .block import KeyboardInterruptInBlock, BlockGenerator


class Cmd(object):
    DIRECT_COMMAND_RE = re.compile(r"^(\d|\"|')+")

    def __init__(self):
        self.stdout = sys.stdout
        self.lineno = 0
        self.block_generator = BlockGenerator(self.read_multi_line)

    def init(self):
        return ""

    def read_multi_line(self, iter_count=1):
        return input(STANDARD_SPACE*iter_count).strip()

    def output(self, message=""):
        self.stdout.write(message+"\n")
        self.stdout.flush()

    def run_direct_command(self, text):
        pass

    def try_run_direct_command(self, text):
        if self.DIRECT_COMMAND_RE.match(text):
            return self.run_direct_command(text)

    def loop(self):
        self.output(self.init())
        while True:
            try:
                self.lineno += 1
                line = input("[{0}] >".format(self.lineno)).strip()
                if not line:
                    continue
                result = self.try_run_direct_command(line) or self._run(line)
                if result:
                    self.output(result)
            except KeyboardInterruptInBlock:
                continue
            except (EOFError, KeyboardInterrupt):
                self.do_exit()

    def _run(self, line):
        def separate(x):
            l = x.split()
            return l[0], l[1:]

        head, args = separate(line)
        try:
            return getattr(self, "do_" + head)(*args)
        except:
            return self.process(self.block_generator.generate(line))

    def process(self, block):
        raise NotImplementedError()

    def do_exit(self, *args):
        self.output("bye")
        sys.exit(0)
