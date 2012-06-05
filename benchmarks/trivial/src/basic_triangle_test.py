# @http://blog.chilly.ca/?p=194

class Triangle(object):
  def __init__(self, a=0, b=0, c=0):
    self.a = a
    self.b = b
    self.c = c

def classify_triangle(triangle):
  a = triangle.a
  b = triangle.b
  c = triangle.c

  a, b, c = sorted([a, b, c])
  if not (a + b) > c:
    return 'notvalid'
  if a == b == c:
    return 'equilateral'
  elif (a == b) or (b == c) or (a == c):
    return 'isoceles'
  else:
    return 'scalene'

def run():
  return classify_triangle(Triangle(2,1,2))

if __name__ == "__main__":
  run()

import unittest

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
