import unittest
from ArgumentProcessor import ArgumentProcessor
import sys

class TestArgumentProcessor(unittest.TestCase):
    #TODO Add tests to make sure invalid input is handled properly
    def parseArgs(self, inp, expectedOut):
        proc = ArgumentProcessor()
        sys.argv = inp
        self.assertEquals(proc.parseCmd(), expectedOut)

    def testNoArgs(self):
        inp = ["fn.py"]
        self.parseArgs(inp, {})
    def testBoolArg(self):
        inp = ["fn.py", "test"]
        self.parseArgs(inp, {"test": True})
    def test2BoolArgs(self):
        inp = ["fn.py", "test1", "test2"]
        self.parseArgs(inp, {"test1": True, "test2": True})
    def testSeed(self):
        inp = ["fn.py", "-seed", "1010"]
        self.parseArgs(inp, {})
    def testSeed3Bools(self):
        inp = ["fn.py", "-seed", "1010", "test1", "test2", "test3"]
        self.parseArgs(inp, {"test1": True, "test2": True, "test3": True})
    def test2BoolSeedBool(self):
        inp = ["fn.py", "test1", "test2", "-seed", "1010", "test1", "test2", "test3"]
        self.parseArgs(inp, {"test1": True, "test2": True, "test3": True})
    def testStringArg(self):
        inp = ["fn.py", "-test1", "one"]
        self.parseArgs(inp, {"test1": "one"})
    def testStringBool(self):
        inp = ["fn.py", "-test1", "one", "test2"]
        self.parseArgs(inp, {"test1": "one", "test2": True})
    def test2StringArgs(self):
        inp = ["fn.py", "-test1", "one", "-test2", "two"]
        self.parseArgs(inp, {"test1": "one", "test2": "two"})
    def testListArg(self):
        inp = ["fn.py", "-test1", "[\"one\", \"two\"]"]
        self.parseArgs(inp, {"test1": ["one", "two"]})
    def testEmptyListArg(self):
        inp = ["fn.py", "-test1", "[]"]
        self.parseArgs(inp, {"test1": []})
    def test2Listargs(self):
        inp = ["fn.py", "-test1", "[\"one\", \"two\"]", "-test2", "[\"three\", \"four\"]"]
        self.parseArgs(inp, {"test1": ["one","two"], "test2": ["three","four"]})
    def testListStringBoolSeed(self):
        inp = ["fn.py", "-test1", "[\"one\"]", "-test2", "two", "test3", "-seed", "1010"]
        self.parseArgs(inp, {"test1": ["one"], "test2": "two", "test3": True})


if __name__ == '__main__':
    unittest.main()