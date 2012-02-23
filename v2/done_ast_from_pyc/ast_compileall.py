import __builtin__
from ast import *
import compileall
import sys
import traceback
import itertools

class RewriteInterpolation(NodeTransformer):
    def __init__(self, filename):
        self.filename = filename
        self.enter_linenos = {}  # id -> (lineno, col_offset)
        self.reach_linenos = {}  # id -> (lineno, col_offset)
        self.counter = itertools.count()
    def visit_Module(self, module_node):
        # Need to import and call ast_report.register_module().
        # These must occur after the "from __future__ import ..." statements.
        # Find where I can insert them.
        body_future = []
        body_rest = []
        for node in module_node.body:
            node = self.visit(node)
            if (not body_rest and isinstance(node, ImportFrom) and
                node.module == "__future__"):
                body_future.append(node)
            else:
                body_rest.append(node)

        # It's easier to let Python convert the code to an AST
        import_line = parse("from ast_report import register_module, check_string").body[0]

        print
        print "module: %r" % self.filename
        print "ast_enter_linenos = %r" % self.enter_linenos
        print "ast_reach_linenos = %r" % self.reach_linenos

        register_line = parse(
            "ast_enter, ast_leave, ast_reached = register_module(%r, %r, %r)" %
            (self.filename, self.enter_linenos, self.reach_linenos)).body[0]

        # Assign a reasonable seeming line number.
        lineno = 1
        if body_future:
            lineno = body_future[0].lineno
        for new_node in (import_line, register_line):
            new_node.col_offset = 1
            new_node.lineno = lineno

        new_body = body_future + [import_line, register_line] + body_rest
        return Module(body=new_body)

    # These are statements which should have an enter and leave
    # (In retrospect, this isn't always true, eg, for 'if')
    def track_enter_leave_lineno(self, node):
        node = self.generic_visit(node)
        id = next(self.counter)
        enter = parse("ast_enter[%d] += 1" % id).body[0]
        leave = parse("ast_leave[%d] += 1" % id).body[0]
        self.enter_linenos[id] = (node.lineno, node.col_offset)
        for new_node in (enter, leave):
            copy_location(new_node, node)

        # This is the code for "if 1: ..."
        n = Num(n=1)
        copy_location(n, node)
        if_node = If(test=n, body=[enter, node, leave], orelse=[])
        copy_location(if_node, node)
        return if_node

    visit_FunctionDef = track_enter_leave_lineno
    visit_ClassDef = track_enter_leave_lineno
    visit_Assign = track_enter_leave_lineno
    visit_AugAssign = track_enter_leave_lineno
    visit_Delete = track_enter_leave_lineno
    visit_Print = track_enter_leave_lineno
    visit_For = track_enter_leave_lineno
    visit_While = track_enter_leave_lineno
    visit_If = track_enter_leave_lineno
    visit_With = track_enter_leave_lineno
    visit_TryExcept = track_enter_leave_lineno
    visit_TryFinally = track_enter_leave_lineno
    visit_Assert = track_enter_leave_lineno
    visit_Import = track_enter_leave_lineno
    visit_ImportFrom = track_enter_leave_lineno
    visit_Exec = track_enter_leave_lineno
    #Global
    visit_Expr = track_enter_leave_lineno
    visit_Pass = track_enter_leave_lineno

    # These statements can be reached, but they change
    # control flow and are never exited.
    def track_reached_lineno(self, node):
        node = self.generic_visit(node)
        id = next(self.counter)
        reach = parse("ast_reached[%d] += 1" % id).body[0]
        self.reach_linenos[id] = (node.lineno, node.col_offset)
        copy_location(reach, node)

        n = Num(n=1)
        copy_location(n, node)
        if_node = If(test=n, body=[reach, node], orelse=[])
        copy_location(if_node, node)
        return if_node

    visit_Return = track_reached_lineno
    visit_Raise = track_reached_lineno
    visit_Break = track_reached_lineno
    visit_Continue = track_reached_lineno
    
    # Some code to instrument the run-time and check for '%' failures.
    def visit_BinOp(self, node):
        if isinstance(node.op, Mod):
            new_node = Call(func=Name(id='check_string', ctx=Load()),
                            args=[node.left, node.right,
                                  Num(n=node.lineno),
                                  Num(n=node.col_offset)],
                            keywords = [], starargs=None, kwargs=None
                            )
            copy_location(new_node, node)
            fix_missing_locations(new_node)
            return new_node
        return node

old_compile = __builtin__.compile

def compile(source, filename, mode, flags=0): # skipping a few parameters
    # My rewrite code uses ast.parse, which ends up calling this
    # function with this argument, so pass it back to the real compile.
    if flags == PyCF_ONLY_AST:
        return old_compile(source, filename, mode, flags)
    assert mode == "exec"
    #traceback.print_stack()
    code = open(filename).read()
    tree = parse(code, filename)
    tree = RewriteInterpolation(filename).visit(tree)
    code = old_compile(tree, filename, "exec")
    return code

# Ugly hack so I can force compileall to use my compile function.
__builtin__.compile = compile
exit_status = int(not compileall.compile_file('sample.py', force=True))
sys.exit(exit_status)
