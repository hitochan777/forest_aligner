import unittest
from NgramLM import NgramLM

class TestNgramLM(unittest.TestCase):

    def test_addNgramCount(self):
        order = 3
        lm = NgramLM(order)
        li = "who knows who can do that ?".split()
        for i in xrange(len(li) - order + 1):
            lm.addNgramCount(li[i:i+order])
        self.assertEqual(len(lm._root.count), len(li) - order + 1)
        self.assertEqual(len(lm._root.children), len(li) - order + 1)
        for i in xrange(order - 2, len(li) - 1):
            self.assertTrue(lm._root.children.has_key(li[i]))

if __name__ == '__main__':
    unittest.main()
