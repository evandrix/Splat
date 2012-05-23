from bytecodehacks.code_gen.method_spec import MethodSpecifier

m = MethodSpecifier("foo_methods")
m.set_template("""\
    def foo(self,arg):
%s""")

print "the whole method from CLASS_1:"
print m.get_method("CLASS_1")
print "just the method body from CLASS_2:"
print m.get_method_body("CLASS_2")
