#from pyREtic slides @ http://prezi.com/jxzw052fcwzn/pyretic-redux-rich-smith/

## Language specific bugs & flaws
class Test:
    var = []
    def __init__(self, x):
        self.var.append(x)
foo = Test(10)
bar = Test(20)

# Class vs. Instance attributes
print foo.var, bar.var

def call_me(args_in = []):
    args_in.append("foo")
    print args_in
call_me(["a", "b", "c"])

# Mutable default arguments
call_me()
call_me()
