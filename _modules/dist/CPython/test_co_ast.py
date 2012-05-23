# In the CPython implementation, to each code object, a new
# attribute `co_ast` was added which contains the related
# AST statement if available.

# This is a simple demonstration for the `co_ast` attribute
# which demonstrates possible meta coding in Python.

import ast, types, sys, copy

def foo(x): return x * 3

def bar(x):
	y = 0
	for i in xrange(10):
		y += foo(i * x)
	return y

print "func:", bar, bar.func_code
print "ast:", bar.func_code.co_ast

print ast.dump(foo.func_code.co_ast)
print ast.dump(bar.func_code.co_ast)
print "bar(5) =", bar(5)

def ast_call_findfunc(astcall):
	assert isinstance(astcall, ast.Call)
	if not isinstance(astcall.func, ast.Name): return None # cannot handle
	funcname = astcall.func.id
	if funcname in globals(): return globals()[funcname]
	if hasattr(__builtins__, funcname): return getattr(__builtins__, funcname)
	return None

def debug_print_funccalls(s):
	if isinstance(s, types.FunctionType):
		print s.func_name, "is calling:"
		s = s.func_code.co_ast
	if isinstance(s, list):
		for c in s:
			debug_print_funccalls(c)
		return
	if isinstance(s, ast.Call):
		f = ast_call_findfunc(s)
		if f is not None:
			print "    calling", f
		else:
			print "    calling", s.func
	for c in ast.iter_child_nodes(s):
		debug_print_funccalls(c)

debug_print_funccalls(bar)

# -----------

def is_arg_const(astarg):
	if isinstance(astarg, ast.Num): return True
	if isinstance(astarg, ast.Str): return True
	# XXX: we might extend this much more...
	return False

def all_args_const(astcall):
	# TODO: also check kwargs, etc.
	return all(map(is_arg_const, astcall.args))

def overwrite_ast_node(n, newnode):
	# delete old fields/attribs
	for a in n._fields + n._attributes:
		delattr(n, a)
	# set class
	n.__class__ = newnode.__class__
	# copy over new
	for a in n._fields + n._attributes:
		setattr(n, a, getattr(newnode, a))

def overwrite_args(n, args):
	if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
		if n.id in args:
			overwrite_ast_node(n, args[n.id])
		return
	for c in ast.iter_child_nodes(n):
		overwrite_args(c, args)

def ast_make_inline_calls(s):
	if isinstance(s, list):
		for c in s:
			ast_make_inline_calls(c)
		return
	for _ in [0]:
		if not isinstance(s, ast.Call): break
		if s.kwargs: break # too complicated :)
		if s.starargs: break
		if s.keywords: break
		callargs = s.args
		f = ast_call_findfunc(s)
		if f is None: break
		if not isinstance(f, types.FunctionType): break
		if not f.func_code.co_ast: break
		funcdef = f.func_code.co_ast
		if funcdef.args.vararg: break # too complicated right now :)
		if funcdef.args.kwarg: break
		funcargs = map(lambda n: n.id, funcdef.args.args)
		assert len(callargs) == len(funcargs)
		funcargs = dict(zip(funcargs, callargs))
		body_first = funcdef.body[0]
		if not isinstance(body_first, ast.Return): break # only very simlpe funcs supported
		fret = copy.deepcopy(body_first.value)
		#print "XX", ast.dump(fret)
		overwrite_ast_node(s, fret)
		#print "XX-", ast.dump(s)
		overwrite_args(s, funcargs)
		#print "XX--", ast.dump(s)
	for c in ast.iter_child_nodes(s):
		ast_make_inline_calls(c)

def compile_func(funcdefast):
	mod = ast.Interactive(body=[funcdefast])
	co = compile(mod, "<recompiled>", "single")
	exec co
	return locals()[funcdefast.name]

def deco_inline_calls(f):
	assert f.func_code.co_ast
	n = copy.deepcopy(f.func_code.co_ast)
	ast_make_inline_calls(n)
	return compile_func(n)

bar = deco_inline_calls(bar)
print ast.dump(bar.func_code.co_ast)
debug_print_funccalls(bar)
print "bar(5) =", bar(5)

# -----------------

def eval_ast(s):
	mod = ast.Expression(body=s)
	co = compile(mod, "<eval_ast>", "eval")
	return eval(co)

def get_const_list(s):
	if not isinstance(s, ast.Call): return
	if not isinstance(s.func, ast.Name): return
	if not s.func.id in ["range", "xrange"]: return
	if not all_args_const(s): return
	l = eval_ast(s)
	make_node = lambda v: ast.Num(n=v, lineno=0, col_offset=0)
	return map(make_node, l)

def ast_make_unroll_staticlooks(s):
	if isinstance(s, list):
		for c in s:
			ast_make_unroll_staticlooks(c)
		return
	for _ in [0]:
		if not isinstance(s, ast.For): break
		if [ bs for bs in s.body if isinstance(bs, ast.Continue) ]: break # continue not supported
		if s.orelse: break # not supported
		constlist = get_const_list(s.iter)
		if not constlist: break
		targetvar = s.target
		body = s.body
		s.__class__ = ast.While
		delattr(s, "target")
		delattr(s, "iter")
		s.test = ast.Name(id="True", ctx=ast.Load(), lineno=0, col_offset=0)
		s.body = []
		for v in constlist:
			s.body.append(ast.Assign(
				targets = [targetvar],
				value = v,
				lineno = 0,
				col_offset = 0
				))
			s.body.extend(body)
		s.body.append(ast.Break(lineno=0, col_offset=0))
	for c in ast.iter_child_nodes(s):
		ast_make_unroll_staticlooks(c)
	
def deco_unroll_staticloops(f):
	assert f.func_code.co_ast
	n = copy.deepcopy(f.func_code.co_ast)
	ast_make_unroll_staticlooks(n)
	return compile_func(n)

bar = deco_unroll_staticloops(bar)
print ast.dump(bar.func_code.co_ast)
print "bar(5) =", bar(5)
