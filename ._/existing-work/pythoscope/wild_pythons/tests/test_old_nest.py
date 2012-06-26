from old_python import OldPython
import unittest
from old_nest import OldNest

class TestOldNest(unittest.TestCase):
    def test_put_hand_returns_sss_sss_SSss_SSss_sss_cough_cough_after_creation_with_list(self):
        old_nest = OldNest([45, 55, 65, 75])
        self.assertEqual('sss sss\nSSss SSss\nsss... *cough* *cough*', old_nest.put_hand())

if __name__ == '__main__':
    unittest.main()
