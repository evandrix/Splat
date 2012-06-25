import unittest
from old_python import OldPython

class TestOldPython(unittest.TestCase):
    def test___init__(self):
        # old_python = OldPython(age)
        assert False # TODO: implement your test here

    def test_hiss(self):
        # old_python = OldPython(age)
        # self.assertEqual(expected, old_python.hiss())
        assert False # TODO: implement your test here

    def test_hiss_returns_sss_cough_cough_after_creation_with_123(self):
        old_python = OldPython(123)
        self.assertEqual('sss... *cough* *cough*', old_python.hiss())

    def test_creation_with_45_raises_value_error(self):
        self.assertRaises(ValueError, lambda: OldPython(45))

    def test_hiss_returns_SSss_SSss_after_creation_with_65(self):
        old_python = OldPython(65)
        self.assertEqual('SSss SSss', old_python.hiss())

    def test_hiss_returns_sss_cough_cough_after_creation_with_75(self):
        old_python = OldPython(75)
        self.assertEqual('sss... *cough* *cough*', old_python.hiss())

    def test_hiss_returns_sss_sss_after_creation_with_55(self):
        old_python = OldPython(55)
        self.assertEqual('sss sss', old_python.hiss())

if __name__ == '__main__':
    unittest.main()
