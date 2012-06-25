def triangle(a,b,c):
    if not (a + b) > c:
        return 'notvalid'
    if a == b == c:
        return 'equilateral'
    elif (a == b) or (b == c) or (a == c):
        return 'isoceles'
    else:
        return 'scalene'