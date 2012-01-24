import unittest
import sys
import sample

class PyUnitframework(unittest.TestCase):
	'''Test Cases generated for sample module'''
# format:
# test_<Test_Number>_<Entity_Name>[<Arg_Status>]<Predicted_Status>_<Comment>
	def test_1_TestClassMethod_WithoutArgs_Pass_With_Only_Valid_Arguments(self):
		sample.TestClass().TestClassMethod()
	def test_2_TestClassMethod_WithArgs_Fail_With_Arg(self):
		self.assertRaises(Exception,sample.TestClass().TestClassMethod,'TestStr0')

if __name__=="__main__":
	testlist=unittest.TestSuite()
	testlist.addTest(unittest.makeSuite(PyUnitframework))
	result = unittest.TextTestRunner(verbosity=2).run(testlist)
	if not result.wasSuccessful():
		sys.exit(1)
	sys.exit(0)
