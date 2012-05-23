"""peak.model ASDL for ASDL"""

from peak.api import *
from peak.util.fmtparse import *
from peak.metamodels.asdl_model import *

ws = MatchString('(?m)(\s*--[^\n]*)*\s*')  # eat whitespace + comments

class TypeID(model.Name):
    mdl_syntax = ExtractString(MatchString('[a-z][A-Za-z0-9_]+'))

class Identifier(model.Name):
    mdl_syntax = ExtractString(MatchString('[A-Za-z][A-Za-z0-9_]+'))

class ConstructorID(model.Name):
    mdl_syntax = ExtractString(MatchString('[A-Z][A-Za-z0-9_]+'))


field.typeName.referencedType = TypeID
field.name.referencedType = Identifier

Id.bounds = 1,1
Id.mdl_syntax = Sequence(field.typeName, ws, Optional(field.name))

Option.bounds = 0,1
Option.mdl_syntax = Sequence(field.typeName, '?', ws, Optional(field.name))

Seq.bounds = 0,None
Seq.mdl_syntax = Sequence(field.typeName, '*', ws, Optional(field.name))

Plus.bounds = 1,None
Plus.mdl_syntax = Sequence(field.typeName, '+', ws, Optional(field.name))

Constructor.name.referencedType = ConstructorID
Constructor.attributes.separator = Sequence(ws, ',', ws)

attribute_names = Sequence('(', ws, Constructor.attributes, ws, ')')

Constructor.mdl_syntax = Sequence(Constructor.name, Optional(attribute_names))


typedef.name.referencedType = TypeID

Sum.types.separator = Sequence(ws,'|',ws)
Sum.attributes.separator = Sequence(ws, ',', ws)
Sum.mdl_syntax = Sequence(
    typedef.name, ws, '=', ws,
    Sum.types,
    Optional(
        ws, 'attributes', ws, attribute_names
    )
)

Product.attributes.separator = Sequence(ws, ',', ws)
Product.mdl_syntax = Sequence(typedef.name, ws, '=', ws, attribute_names)

module.name.referencedType    = Identifier
module.definitions.separator  = ws
module.definitions.sepMayTerm = True

module.mdl_syntax = Sequence(
    ws, 'module', ws, module.name, ws,
    '{', ws, module.definitions, '}', ws
)


















def write_module(self, strm):

    print >>strm, "from peak.api import model"
    print >>strm

    for defn in self.definitions:
        defn.write(strm)

module.write = write_module


def write_Product(self, strm):

    print >>strm, "class %s(model.Struct):" % self.name
    print >>strm

    strm.push(1)

    try:
        posn = 1
        for attr in self.attributes:
            attr.write(strm,posn)
            posn += 1
    finally:
        strm.pop()

    print >>strm
    print >>strm

Product.write = write_Product











def write_Sum(self,strm):

    print >>strm, "class %s(model.Struct):" % self.name
    print >>strm

    strm.push(1)

    try:
        print >>strm,"mdl_isAbstract = True"
        print >>strm

        posn = 1
        for attr in self.attributes:
            attr.write(strm,posn)
            posn += 1

        # write mdl_subclassNames
        print >>strm,"mdl_subclassNames = ("
        strm.push(1)
        try:
            for c in self.types:
                print >>strm, '%r,' % c.name
        finally:
            strm.pop()
        print >>strm,")"

    finally:
        strm.pop()

    print >>strm
    print >>strm

    for c in self.types:
        c.write(strm, posn, self)

Sum.write = write_Sum





def write_Constructor(self, strm, posn, base):

    print >>strm, "class %s(%s):" % (self.name, base.name)

    if self.attributes:

        print >>strm
        strm.push(1)

        try:
            for attr in self.attributes:
                attr.write(strm,posn)
                posn = posn + 1

        finally:
            strm.pop()

        print >>strm

    else:
        print >>strm, "    pass"

    print >>strm

Constructor.write = write_Constructor
















def write_field(self, strm, posn):

    print >>strm, "class %s(model.structField):" % self.name
    strm.push(1)

    try:
        typeName = {
            'identifier':'model.Name',
            'string':'model.String',
            'integer':'model.Integer'
        }.get(self.typeName,`self.typeName`)

        print >>strm, "referencedType = %s" % typeName
        if self.bounds[0]<>0:
            print >>strm, "lowerBound = %r" % self.bounds[0]
        if self.bounds[1]<>1:
            print >>strm, "upperBound = %r" % self.bounds[1]
        print >>strm, "sortPosn = %d" % posn

    finally:
        strm.pop()

    print >>strm


field.write = write_field















class ModelGenerator(running.commands.AbstractCommand):

    """Generate a domain model module from an .asdl file"""

    def _run(self):

        infile, outfile = self.argv[1:]
        ast = module.mdl_fromString(open(infile,'rt').read())

        from peak.util.IndentedStream import IndentedStream
        out = IndentedStream(open(outfile,'wt'))

        print >>out, "# Automatically generated from %s" % infile
        print >>out
        ast.write(out)
        out.close()


if __name__=='__main__':

    cmd = ModelGenerator(
        config.makeRoot(),
        argv = [
            '', 'peak/metamodels/ASDL.asdl', 'peak/metamodels/asdl_model2.py'
        ],
    )

    cmd.run()













