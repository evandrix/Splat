"""Relational Algebra"""

from peak.api import *
from peak.util.hashcmp import HashAndCompare
import interfaces
from interfaces import *
from kjbuckets import kjSet, kjGraph
from copy import deepcopy, _deepcopy_dispatch
from cStringIO import StringIO
__all__ = []

def _dc_kjGraph(x,memo):
    return kjGraph([(deepcopy(k,memo),deepcopy(v,memo)) for k,v in x.items()])

def _dc_kjSet(x,memo):
    return kjSet([deepcopy(k,memo) for k in x.items()])

_deepcopy_dispatch[type(kjSet())] = _dc_kjSet
_deepcopy_dispatch[type(kjGraph())] = _dc_kjGraph






















class AbstractSQLRenderable:

    protocols.advise(
        instancesProvide = [ISQLRenderable],
    )

    def sqlCondition(self,writer):
        raise TypeError("Not a condition",self)

    def sqlExpression(self,writer):
        raise TypeError("Not an expression",self)

    def sqlSelect(self,writer):
        raise TypeError("Not SELECT-able",self)

    def sqlTableRef(self,writer):
        writer.write('(')
        writer.writeSelect(self)
        writer.write(')')


class Parameter(AbstractSQLRenderable):

    def __init__(self,name):
        self.name = name

    def sqlExpression(self,writer):
        writer.namedParam(self)













class _expr(AbstractSQLRenderable):

    protocols.advise(
        instancesProvide = [IBooleanExpression],
    )

    def conjuncts(self):
        return [self]

    def disjuncts(self):
        return [self]

    def __invert__(self):
        return Not(self)

    def __and__(self,other):
        if self==other or other is EMPTY:
            return self
        return And(self,other)

    def __or__(self,other):
        if self==other or other is EMPTY:
            return self
        return Or(self,other)

















class EMPTY(binding.Singleton):

    protocols.advise(
        classProvides = [IBooleanExpression, ISQLRenderable],
    )

    def conjuncts(self):
        return ()

    def disjuncts(self):
        return ()

    def __invert__(self):
        return self

    def __and__(self,other):
        return other

    def __or__(self,other):
        return other

    def sqlCondition(self,writer):
        pass

    def sqlExpression(self,writer):
        raise TypeError("Not an expression/SELECT-able",self)

    sqlSelect = sqlTableRef = sqlExpression













class PhysicalDB(binding.Component):

    tables = binding.Make(list)

    tableMap = binding.Make(
        lambda self: dict(
            [(name,Table(name,columns,self)) for name,columns in self.tables]
        )
    )

    def __getitem__(self,name):
        return self.tableMap[name]

    def __getattr__(self,attr):
        if not attr.startswith('_') and attr in self.tableMap:
            return self[attr]
        raise AttributeError,attr
























class SQLWriter(binding.Component):

    protocols.advise(
        instancesProvide=[ISQLWriter]
    )

    counter = binding.Make(lambda: [1])
    aliases = binding.Make(dict)
    stream  = binding.Make(lambda: StringIO())
    params  = binding.Make(list)
    write   = getvalue = binding.Delegate('stream')

    renderingProtocol = ISQLRenderable

    def writeExpr(self,ob):
        v = adapt(ob,self.renderingProtocol,None)
        if v is None:
            self.write(`ob`)
        else:
            v.sqlExpression(self)

    def writeCond(self,ob):
        adapt(ob,self.renderingProtocol).sqlCondition(self)

    def writeSelect(self,ob):
        adapt(ob,self.renderingProtocol).sqlSelect(self)

    def writeTable(self,RV):
        adapt(RV,self.renderingProtocol).sqlTableRef(self)
        self.write(" AS ")
        self.write(self.getAlias(RV))

    def writeAlias(self,RV):
        self.write(self.getAlias(RV))







    def getAlias(self,rv):
        return self.aliases[rv]

    def assignAlias(self,rv):
        if rv in self.aliases:
            return
        n0 = getattr(rv,'name','*')[0]
        if n0.isalpha():
            ltr = n0.upper()
        else:
            ltr="x"
        self.aliases[rv] = "%s%d" % (ltr,self.counter[0])
        self.counter[0] += 1

    def assignAliasesFor(self,query):
        rvs = list(query.getInnerRVs())+list(query.getOuterRVs()) # XXX nested
        rvs.sort()
        map(self.assignAlias,rvs)

    def namedParam(self,param):
        self.write('?')
        self.params.append(param)

    def data(self):
        return self.getvalue(), self.params

    def prepender(self, pre):
        return ContextProxy(writer=self,prepend=pre)

    def separator(self,s):
        flag = [1]

        def write():
            if flag:
                flag.pop()
            else:
                self.write(s)

        return write


class ContextProxy(SQLWriter):

    writer = None
    prepend = None

    getAlias = assignAlias = assignAliasesFor = data = params = \
        binding.Delegate('writer')

    def write(self,s):

        write = self.writer.write

        if self.prepend:
            write(self.prepend)
            del self.prepend

        self.write = write
        write(s)























class AbstractRV(AbstractSQLRenderable,object):

    protocols.advise(
        instancesProvide = [IRelationVariable]
    )

    condition = EMPTY
    outers = ()

    def __call__(self,
        where=None,join=(),outer=(),rename=(),keep=None,calc=(),groupBy=()
    ):
        cols = kjGraph(self.columns)
        rename = ~kjGraph(rename)
        groupBy = kjSet(groupBy)
        join = [self]+list(join)
        outer = list(outer)

        if where is None:
            where = EMPTY

        for rv in join+outer:
            cols += rv.attributes()

        if groupBy or keep is not None:
            cols = (kjSet(keep or ())+kjSet(~rename)+groupBy) * cols

        if rename:
            cols = rename * cols + (cols-cols.restrict(~rename))

        rv = BasicJoin(
            where, join, outer, cols+kjGraph(calc)
        )

        if groupBy:
            return GroupBy(rv, groupBy.items())

        return rv



    def attributes(self):
        return self.columns

    def getInnerRVs(self):
        return (self,)

    def getOuterRVs(self):
        return self.outers

    def getCondition(self):
        return self.condition

    def __getitem__(self,key):
        return self.columns[key]

    def keys(self):
        return self.columns.keys()

    def __getattr__(self,attr):
        if not attr.startswith('_') and self.columns.has_key(attr):
            return self.columns[attr]
        raise AttributeError,attr

    def clone(self):
        return deepcopy(self)
















class Table(AbstractRV, HashAndCompare):

    def __init__(self,name,columns,db=None):
        self.name = name
        self.columns = kjGraph([(c,Column(c,self)) for c in columns])
        self.db = db
        self._hashAndCompare = (
            self.__class__.__name__, self.db, self.name
        )

    def __repr__(self):
        return self.name

    def getDB(self):
        return self.db

    def sqlSelect(self,writer):
        writer.write("SELECT * FROM %s" % self.name)
        return writer.data()

    def sqlTableRef(self,writer):
        writer.write(self.name)

    def __deepcopy__(self,memo):
        # Avoid deepcopying self.db
        newself = self.__class__(self.name,(),self.db)
        memo[id(newself)] = newself
        newself.columns = deepcopy(self.columns,memo)
        return newself












class GroupBy(AbstractRV, HashAndCompare):

    def __init__(self,rv,groupBy,cond=EMPTY):
        self.condition = cond
        groupBy = list(groupBy); groupBy.sort()
        self.rv = rv
        self.groupBy = groupBy
        self.columns = kjGraph([(c,Column(c,self)) for c in rv.keys()])
        for k in rv.keys():
            if k not in groupBy and not rv[k].isAggregate():
                raise TypeError("Non-aggregate column in groupBy",k,rv[k])
        self._hashAndCompare = (
            self.__class__.__name__, rv, tuple(groupBy)
        )

    def getDB(self):
        return self.rv.getDB()

    def sqlSelect(self,writer):
        writer.assignAliasesFor(self.rv)
        writer.writeSelect(self.rv)
        writer.write(' GROUP BY ')
        sep = writer.separator(', ')

        for col in self.groupBy:
            sep()
            writer.writeExpr(self.rv[col])

        writer.prepender(' HAVING ').writeCond(self.condition)
        return writer.data()

    def __call__(self, where=None,**kw):
        if kw:
            kw['where']=where
            return super(GroupBy,self).__call__(**kw)
        if where is not None:
            return GroupBy(self.rv,self.groupBy,self.condition&where)
        return self



class AbstractDV(AbstractSQLRenderable):

    protocols.advise(
        instancesProvide = [IDomainVariable]
    )

    _agg = False

    def eq(self,dv):
        return Cmp(self,'=',dv)

    def ne(self,dv):
        return Cmp(self,'<>',dv)

    def lt(self,dv):
        return Cmp(self,'<',dv)

    def ge(self,dv):
        return Cmp(self,'>=',dv)

    def gt(self,dv):
        return Cmp(self,'>',dv)

    def le(self,dv):
        return Cmp(self,'<=',dv)

    def isAggregate(self):
        return self._agg













class Column(AbstractDV,HashAndCompare):

    protocols.advise(
        instancesProvide = [IRelationAttribute]
    )

    def __init__(self,name,table):
        self.name, self.table = name, table
        self._hashAndCompare = (
            self.__class__.__name__, self.table, self.name
        )

    def getRV(self):
        return self.table

    def getDB(self):
        return self.table.getDB()

    def sqlExpression(self,writer):
        writer.write(writer.getAlias(self.table)+'.'+self.name)





















class Func(AbstractDV):
    isAggFunc = False

    def __init__(self,name,*args):

        self.fname = name
        self.args = args
        agg = None

        for arg in args:
            arg = adapt(arg,IDomainVariable,None)
            if arg is not None:
                if agg is None:
                    agg = arg.isAggregate()
                elif agg<>arg.isAggregate():
                    raise TypeError(
                        "Mixed aggregate/non-aggregate arguments",args
                    )

        if agg and self.isAggFunc:
            raise TypeError("Can't aggregate an aggregate",args)

        self._agg = agg or self.isAggFunc


    def sqlExpression(self,writer):
        writer.write(self.fname); writer.write('(')
        sep = writer.separator(',')
        for arg in self.args:
            sep(); writer.writeExpr(arg)
        writer.write(')')

class Aggregate(Func):
    isAggFunc = True

def function(name):
    return lambda *args: Func(name,*args)

def aggregate(name):
    return lambda *args: Aggregate(name,*args)

class BasicJoin(AbstractRV, HashAndCompare):

    def __init__(self,condition,relvars,outers=(),columns=()):
        myrels = []
        relUsage = {}

        def checkUsage(rv):
            r = id(rv)
            if r in relUsage:
                raise ValueError("Relvar used more than once",rv)
            else:
                relUsage[r]=True
            return rv

        outers = map(checkUsage,outers)

        for rv in relvars:
            myrels.extend(map(checkUsage,rv.getInnerRVs()))
            outers.extend(map(checkUsage,rv.getOuterRVs()))
            condition = condition & rv.getCondition()

        if len(myrels)<1:
            raise TypeError("BasicJoin requires at least 1 relvar")

        myrels.sort()
        outers.sort()
        self.relvars = tuple(myrels)
        self.outers = tuple(outers)
        self.condition = condition
        self.columns = kjGraph(columns)
        self._hashAndCompare = (
            self.__class__.__name__, condition,
            self.relvars, self.outers, self.columns
        )







    def __repr__(self):
        parms=(
            self.condition, list(self.relvars), list(self.outers),
            list(self.columns.items())
        )
        return '%s%r' % (self._hashAndCompare[0], parms)


    def getInnerRVs(self):
        return self.relvars


    def getDB(self):
        db = self.relvars[0].getDB()
        for rv in self.relvars[1:]:
            if rv.getDB() is not db:
                return None
        return db























    def sqlSelect(self,writer):
        writer.assignAliasesFor(self)
        writer.write('SELECT ')
        sep = writer.separator(', ')
        remainingColumns = self.columns

        for tbl in self.relvars:

            tblCols = tbl.attributes()
            outputSubset = remainingColumns * kjSet(tblCols.values())
            remainingColumns = remainingColumns - outputSubset

            if outputSubset==tblCols:
                # All names in table are kept as-is, so just use '*'
                sep(); writer.writeAlias(tbl); writer.write(".*")
                continue

            # For all output columns that are in this table...
            for name,col in outputSubset.items():
                sep()
                writer.writeExpr(col)
                if name<>col.name:  # XXX!!!
                    writer.write(' AS ')
                    writer.write(name)

        for name,col in remainingColumns.items():
            sep()
            writer.writeExpr(col); writer.write(' AS '); writer.write(name)

        writer.write(' FROM ')
        sep = writer.separator(', ')
        for tbl in self.relvars:
            sep(); writer.writeTable(tbl)

        writer.prepender(' WHERE ').writeCond(self.condition)
        return writer.data()





class _compound(_expr,HashAndCompare):

    def __init__(self,*args):

        operands = {}

        for op in args:
            for item in self._getPromotable(op):
                operands[item]=1

        operands = list(operands)
        operands.sort()
        self.operands = tuple(operands)

        if len(operands)<2:
            raise TypeError,"Compounds require more than one operand"

        self._hashAndCompare = self.__class__.__name__, self.operands


    def __repr__(self):
        return '%s%r' % self._hashAndCompare



















class And(_compound):

    def _getPromotable(self,op):
        return adapt(op,IBooleanExpression).conjuncts()

    def conjuncts(self):
        return self.operands

    def __invert__(self):
        return Or(*tuple([~op for op in self.operands]))

    def sqlCondition(self,writer):
        sep = writer.separator(' AND ')
        for op in self.operands:
            sep()
            writer.writeCond(op)


class Or(_compound):

    def _getPromotable(self,op):
        return adapt(op,IBooleanExpression).disjuncts()

    def disjuncts(self):
        return self.operands

    def __invert__(self):
        return And(*tuple([~op for op in self.operands]))

    def sqlCondition(self,writer):
        writer.write('(')
        sep = writer.separator(' OR ')
        for op in self.operands:
            sep()
            writer.writeCond(op)
        writer.write(')')





class Not(_compound):

    def __init__(self,operand):
        self.operands = operand,
        self._hashAndCompare = self.__class__.__name__, self.operands

    def __invert__(self):
        return self.operands[0]

    def sqlCondition(self,writer):
        writer.write('NOT (')
        writer.writeCond(self.operands[0])
        writer.write(')')




























class Cmp(_expr, HashAndCompare):

    invOps = {'=':'<>', '<':'>=', '>':'<='}
    invOps = kjGraph(invOps.items())
    invOps = invOps + ~invOps

    def __init__(self,arg1,op,arg2):
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2
        self._hashAndCompare = op,arg1,arg2

    def __invert__(self):
        try:
            revOp = self.invOps[self.op]
        except KeyError:
            return Not(self)
        else:
            return self.__class__(self.arg1,revOp,self.arg2)

    def __repr__(self):
        return 'Cmp%r' % ((self.arg1,self.op,self.arg2),)

    def sqlCondition(self,writer):
        writer.writeExpr(self.arg1)
        writer.write(self.op)
        writer.writeExpr(self.arg2)














