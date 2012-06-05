from codeutils import delegate_code

## Test additional behavior before and after

def test():
    print "test"

def delegatee(f,args,kw):
    print ">", f, args, kw
    f(*args,**kw)
    print "<", f

delegate_code(test, delegatee)
test()

del test, delegatee

## Test manipulating the arguments

def test(a):
    print "test", a

def delegatee(f,args,kw):
    a = args[0]
    f(a ** 2)

delegate_code(test, delegatee)
test(5)

del test, delegatee

## Test generators

def test():
    yield 1
    yield 2
    yield 3

def delegatee(f, args, kw):
    return iter(['a','b','c'])

delegate_code(test, delegatee)
for x in test():
    print x

## Real-world example

from string import Template

# Define your new behaviour
global_subst_kws = {'x': 'X'}
def substitute_delegatee(f,args,kw):
    kw.update(global_subst_kws)
    return f(*args,**kw)
 
# Apply the new behavior to Template's substitution methods
delegate_code([Template.substitute, Template.safe_substitute],
              substitute_delegatee)
 
# Test the new behavior
print Template("$x and $y").substitute({'x': '1', 'y': '2'}) # => X and 2
print Template("$x and $z").safe_substitute({'z': '3'})      # => X and 3
