class Triangle(object):
    a = b = c = 0
    def __init__(self, a=0, b=0, c=0):
        self.a = a
        self.b = b
        self.c = c

def classify_triangle(triangle):
    a, b, c = sorted([triangle.a, triangle.b, triangle.c])
    if not (a + b) > c:
        return 'invalid'
    if a == b == c:
        return 'equilateral'
    if (a == b) or (b == c) or (a == c):
        return 'isoceles'
    else:
        return 'scalene'

if __name__ == "__main__":
    classify_triangle(Triangle(3, 4, 5))
