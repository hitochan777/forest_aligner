import unittest
from scripts import combineSP

class TestCombineSP(unittest.TestCase):

    def test_combineLine(self):
        sline = "1-2 3-3 2-1"
        spline = "1-2 3-3 2-1 5-1 1-1"
        result = combineSP.combineLine(sline, spline)
        self.assertEqual(set(["1-2[S]", "3-3[S]", "2-1[S]", "5-1[P]", "1-1[P]"]), set(result.split(" ")))

if __name__ == '__main__':
    unittest.main()
