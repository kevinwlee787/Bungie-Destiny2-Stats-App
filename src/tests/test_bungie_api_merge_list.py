import sys
import pathlib

sys.path.insert(1, str(pathlib.Path().absolute()) + '\\')

from src.bungie_api.bungieD2_api import *
import unittest

class TestMergeList(unittest.TestCase):

    def test_intMerge(self):
        l1 = [12, 8, 7, 4, 3]
        l2 = [11, 9, 2]
        l3 = [10, 6, 5, 1]
        def cmp(x, y):
            return x > y
        expected = [12, 11, 10, 9, 8]
        merged = merge_list(5, l1, l2, l3, cmp)
        self.assertEqual(expected, merged)

    def test_intMergeFull(self):
        l1 = [12, 8, 7, 4, 3]
        l2 = [11, 9, 2]
        l3 = [10, 6, 5, 1]
        
        expected = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        merged = merge_list(12, l1, l2, l3, lambda x, y: x > y)
        self.assertEqual(expected, merged)

    def test_merge2(self):
        l1 = [12, 8, 7, 4, 3]
        l2 = [11, 9, 2]
        
        expected = [12, 11, 9, 8, 7, 4, 3, 2]
        merged = merge_list(8, l1, l2, [], lambda x, y: x > y)
        self.assertEqual(expected, merged)

    def test_strBasic(self):
        l1 = ['zz', 'zd']
        l2 = ['c', 'b', 'a']
        l3 = ['zx', 'zc', 'za', 'd']

        expected = ['zz', 'zx', 'zd', 'zc', 'za', 'd', 'c', 'b', 'a']
        merged = merge_list(9, l1, l2, l3, lambda x, y: x > y)
        self.assertEqual(expected, merged)

        

if __name__ == '__main__':
    unittest.main()