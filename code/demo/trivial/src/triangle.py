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
