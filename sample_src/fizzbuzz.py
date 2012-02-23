# fizzbuzz.py
for i in range(1, 10):
    if i % 15 == 0:
        print i, "fizzbuzz"
    elif i % 5 == 0:
        print i, "buzz"
    elif i % 3 == 0:
        print i, "fizz"
    else:
        print i
