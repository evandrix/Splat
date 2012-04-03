import regres

@regres.regres
def do_something(a, this=1):
	return a[1]

do_something("Hi\nno")
print regres.run_regression(do_something, "Hi\nno")
