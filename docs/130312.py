class Test(object):
    def foo(self,a,b,c):
        self.foo = 5
        print self.foo
        return self.foo(a,b,c)

def bar():
    return bar()

def strcmp():
    guess = "a"
    correct = "b"
    if guess == correct:
        print "That's it!\n"

