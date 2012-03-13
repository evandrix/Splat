# @ http://en.literateprograms.org/Fibonacci_numbers_%28Python%29

def fib_recursive(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib_recursive(n-1) + fib_recursive(n-2)

memo = {0:0, 1:1}        
def fib_memo(n):
    if not n in memo:
        memo[n] = fib_memo(n-1) + fib_memo(n-2)
    return memo[n]

def fib_iteration(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a

def fib_gen():
    a, b = 0, 1
    while 1:
        yield a
        a, b = b, a + b

# fails when n >= 70
phi = (1 + 5**0.5) / 2
def fib_binet(n):
    return int(round((phi**n - (1-phi)**n) / 5**0.5))
    
from math import log
def fibinv(f):
    if f < 2:
        return f
    return int(round(log(f * 5**0.5) / log(phi)))

def mul(A, B):
    a, b, c = A
    d, e, f = B
    return a*d + b*e, a*e + b*f, b*e + c*f
def pow(A, n):
    if n == 1:     return A
    if n & 1 == 0: return pow(mul(A, A), n//2)
    else:          return mul(A, pow(mul(A, A), (n-1)//2))
def fib_matrix(n):
    if n < 2: return n
    return pow((1,1,0), n-1)[0]

def powLF(n):
    if n == 1:     return (1, 1)
    L, F = powLF(n//2)
    L, F = (L**2 + 5*F**2) >> 1, L*F
    if n & 1:
        return ((L + 5*F)>>1, (L + F) >>1)
    else:
        return (L, F)
def fibLF(n):
    if n & 1:
        return powLF(n)[1]
    else:
        L, F = powLF(n // 2)
        return L * F

fibs = {0: 0, 1: 1}
def fib_ewd(n):
    if n in fibs: return fibs[n]
    if n % 2 == 0:
        fibs[n] = ((2 * fib((n / 2) - 1)) + fib(n / 2)) * fib(n / 2)
        return fibs[n]
    else:
        fibs[n] = (fib((n - 1) / 2) ** 2) + (fib((n+1) / 2) ** 2)
        return fibs[n]
