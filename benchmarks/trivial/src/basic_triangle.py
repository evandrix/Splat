# @http://blog.chilly.ca/?p=194
import unittest
class Triangle(object):
    a = 0
    def __init__(self, a=0, b=0, c=0):
        self.a = a
        self.b = b
        self.c = c

def classify_triangle(a,b,c):
    triangle = Triangle(a,b,c)
    a,b,c = sorted([triangle.a, triangle.b, triangle.c])
    if not (a + b) > c:
        return 'notvalid'
    if a == b == c:
        return 'equilateral'
    elif (a == b) or (b == c) or (a == c):
        return 'isoceles'
    else:
        return 'scalene'
def run(triangle,used_0,unused_1,default_2='def'):
    temp_value = used_0 + default_2 - 5
    classify_triangle(triangle.a, triangle.b, triangle.c)
def fib_recursive(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib_recursive(n-1) + fib_recursive(n-2)

class ClassifyTriangleTest(unittest.TestCase):
    def testEquilateral(self):
        result = classify_triangle(2, 2, 2)
        self.assertEquals(result, 'equilateral')
    def testIsoceles(self):
        result = classify_triangle(2, 2, 1)
        self.assertEquals(result, 'isoceles')
        result = classify_triangle(2, 1, 2)
        self.assertEquals(result, 'isoceles')
        result = classify_triangle(1, 2, 2)
        self.assertEquals(result, 'isoceles')
    def testInvalidIsoceles(self):
        result = classify_triangle(1, 1, 10)
        self.assertEquals(result, 'notvalid')
    def testInvalidScalene(self):
        result = classify_triangle(1, 2, 5)
        self.assertEquals(result, 'notvalid') 
    def testScalene(self):
        result = classify_triangle(3, 4, 5)
        self.assertEquals(result, 'scalene')
if __name__ == '__main__':
    unittest.main()

