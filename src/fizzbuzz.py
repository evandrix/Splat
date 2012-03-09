def fizzbuzz(n):
    for i in xrange(n):
        if i % 15 == 0:
            print i, "fizzbuzz"
        elif i % 5 == 0:
            print i, "buzz"
        elif i % 3 == 0:
            print i, "fizz"
        else:
            print i
