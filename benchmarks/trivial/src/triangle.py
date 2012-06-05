class FakeTriangle(object):
  def __init__(self, a=0, b=0, c=0):
    self.a = a
    self.b = b
    self.c = c

class Triangle(object):
  def __init__(self, a=0, b=0, c=0):
    self.a = a
    self.b = b
    self.c = c

  def non_internal_method(self):
    pass

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

def run(a,b,c):
  return classify_triangle(Triangle(a,b,c))

if __name__ == "__main__":
    print run(2,1,2)
    print classify_triangle(FakeTriangle(2,1,2))

