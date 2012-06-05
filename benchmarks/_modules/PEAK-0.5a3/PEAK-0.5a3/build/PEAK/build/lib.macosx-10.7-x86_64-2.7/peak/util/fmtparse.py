"""Parsing and formatting based on production rules

 This module provides some special parsing and formatting features not found
 in other Python parsing libraries.  Specifically it:

    * supports reversing the production process to convert parsed output back
      to a canonical version of the input

    * Supports "smart tokenizing" based on contextually-available delimiters

    * does not separate "lexing" or "tokenizing" from "parsing", so lexical
      analysis can be parse-context dependent

    * uses "Packrat Parsing" for fast recursive-descent parsing with arbitrary
      lookahead depths (see http://www.pdos.lcs.mit.edu/~baford/packrat/ for
      more on this innovative approach)

    * is designed to accomodate parsing things other than strings (e.g. object
      streams, SAX event lists,...?)

    * allows the definition of arbitrary "rule", "input" and "state" objects
      that can be fitted into the framework to handle specialized input types,
      context passing, etc.

 The first four features were critical requirements for PEAK's URL-parsing
 tools.  We wanted to make it super-easy to create robust URL syntaxes that
 would produce canonical representations of URLs from input data as well as
 sensibly parse input strings.  And part of "super-easy" meant not having
 to write bazillions of regular expressions to parse every field in a URL.

 Limitations:

    - The framework isn't designed for "formatting" to non-strings.
      Specifically, most rules assume that their sub-rules will only
      'write()' things that can be joined with '"".join()' when formatting.

    - Some parts of the framework may not be 100% Unicode-safe, even if a
      UnicodeInput type were implemented.  Code review and patches appreciated.

 TODO:

    * Docstrings, docstrings, docstrings...  and a test suite!

    * ParseError should provide line/column info about the error location, not
      just offset, and it should be provided by input.error() rather than by
      the rule signalling the error.  Of course, all the rules should be
      calling input.error() instead of creating ParseError instances...

    * Perform timing tests and investigate parsing speedups for:

        - "Compiling" rules to regular expressions + postprocessors

        - "Optimizing" rules (e.g. convert Optional(user, '@') to something
          that forward-scans for '@' before trying to match 'user').

        - Moving speed-critical parts to C
"""

from peak.util.symbols import NOT_GIVEN
import protocols; from protocols import adapt

import re

__all__ = [
    'ParseError', 'MissingData', 'Rule', 'Sequence', 'Repeat', 'Optional',
    'Tuple', 'Named', 'ExtractString', 'Conversion', 'Alternatives',
    'Set', 'MatchString', 'parse', 'format', 'Input', 'StringInput',
    'StringConstant', 'Epsilon', 'IRule', 'IInput',
]

class ParseError(Exception):
    pass

class MissingData(Exception):
    pass

from peak.binding.once import Make  # XXX Core being used in a utility!

def uniquechars(s):
    return ''.join(dict([(c,c) for c in s]))


class IRule(protocols.Interface):

    """Production rule protocol for translation between data and strings"""

    def parse(input, produce, startState):
        """Parse 'input' at 'startState', call 'produce(result)', return state

        Return a 'ParseError' instance if no match"""

    def format(data, write):
        """Pass formatted 'data' to 'write()'"""

    def withTerminators(terminators, memo):
        """Return a version of this syntax using the specified terminators"""

    def getOpening(closing, memo):
        """Possible opening characters for this match, based on 'closing'"""


protocols.declareAdapter(
    lambda o,p: StringConstant(o),
    provides=[IRule],
    forTypes=[str]
)

protocols.declareAdapter(
    lambda o,p: Optional(*o),
    provides=[IRule],
    forTypes=[tuple]
)











class Rule(object):

    """Production rule protocol for translation between data and strings"""

    protocols.advise(
        instancesProvide=[IRule]
    )

    __slots__ = ()

    def parse(self, input, produce, startState):
        raise NotImplementedError

    def format(self, data, write):
        raise NotImplementedError

    def withTerminators(self, terminators, memo):
        raise NotImplementedError

    def getOpening(self,closing,memo):
        raise NotImplementedError




















class IInput(protocols.Interface):

    def reset():
        """"""

    def parse(rule,produce,state):
        """"""

    def error(rule,state,*args):
        """"""

    def startState():
        """"""

    def finished(state):
        """"""


protocols.declareAdapter(
    lambda o,p: StringInput(o),
    provides=[IInput],
    forTypes=[str]
)


















class Input(object):

    protocols.advise(
        instancesProvide=[IInput]
    )

    def __init__(self, *__args,**__kw):
        super(Input,self).__init__(*__args,**__kw)
        self.reset()

    def reset(self):
        self.memo = {}

    def parse(self, rule, produce, state):

        key = rule, state
        memo = self.memo

        if key in memo:
            state, result = memo[key]
        else:
            result = []
            state = rule.parse(self, result.append, state)
            memo[key] = state, result

        map(produce,result)
        return state


    def error(self, rule, state, *args):
        return ParseError(rule=rule, state=state, *args)

    def startState(self):
        raise NotImplementedError

    def finished(self,state):
        raise NotImplementedError




class Epsilon(Rule):

    """Simplest possible rule: matches nothing, formats nothing"""

    def parse(self, input, produce, startState):
        return startState

    def format(self,data,write):
        pass

    def withTerminators(self,terminators,memo):
        return self

    def getOpening(self,closing,memo):
        return closing


























class Sequence(Rule):

    closingChars = ''

    def __init__(self, *__args, **__kw):
        self.__dict__.update(__kw)
        self.initArgs = __args

    def parse(self, input, produce, startState):

        state = startState
        data = []

        for rule in self.rules:
            state = input.parse(rule, data.append, state)
            if isinstance(state,ParseError):
                return state

        map(produce, data)
        return state

    def format(self, data, write):
        for rule in self.rules:
            rule.format(data,write)


    def withTerminators(self, terminators, memo):
        key = id(self), terminators
        if key in memo:
            return memo[key][0]

        r = self.__class__(*self.initArgs, **{'closingChars':terminators})
        memo[key] = r, self
        r._computeRules(memo)
        return r

    def getOpening(self,closing,memo):
        if 'rules' not in self.__dict__:
            self._computeRules(memo)
        return self.openingChars

    def _computeRules(self, memo=None):

        obs = [adapt(ob,IRule) for ob in self.initArgs]

        obs.reverse()

        closeAll = self.closingChars
        closeCtx = ''

        syn = []
        self.__dict__.setdefault('rules',syn)

        if not memo:
            memo = { (id(self),closeAll): (self, self) }

        if obs:
            self.openingChars = obs[-1].getOpening('',memo)

        for ob in obs:
            terms = uniquechars(closeAll+closeCtx)
            key = id(ob), terms
            if key in memo:
                ob = memo[key][0]
            else:
                ob = ob.withTerminators(terms, memo)
                memo[key] = ob, self
            closeCtx = ob.getOpening(closeCtx,memo)
            syn.append(ob)

        self.openingChars = closeCtx
        syn.reverse()
        self.rules = syn
        return syn

    rules = Make(lambda self: self._computeRules(), attrName='rules')

    openingChars = ''




class Optional(Sequence):

    """Wrapper that makes a construct optional"""

    def parse(self, input, produce, startState):
        state = input.parse(super(Optional,self),produce,startState)
        if isinstance(state,ParseError):
            return startState
        return state

    def format(self, data, write):

        """Return a value if any non-empty non-constant parts"""

        out = []
        const = []

        for rule in self.rules:

            try:
                rule.format(data,out.append)
            except MissingData:
                out.append('')

            if isinstance(rule,str):
                const.append(rule)

        if ''.join(out) != ''.join(const):
            # output if there are any "variable" contents
            map(write,out)

    def getOpening(self,closing,memo):
        if 'rules' not in self.__dict__:
            self._computeRules(memo)
        return self.openingChars+closing






class StringConstant(Rule, str):

    def __new__(klass, value, caseSensitive=True):
        self=super(StringConstant,klass).__new__(klass,value)
        self.caseSensitive = caseSensitive
        return self

    def parse(self, inputStr, produce, startState):

        state = startState+len(self)
        if self.caseSensitive:
            if inputStr[startState:state]==self:
                return state
        elif inputStr[startState:state].lower()==self.lower():
            return state

        return ParseError(
            "Expected %r, found %r at position %d in %r" %
            (self, inputStr[startState:state], startState, inputStr)
        )


    def format(self,data,write):
        write(self)


    def withTerminators(self,terminators,memo):
        return self


    def getOpening(self,closing,memo):
        if self:
            if self.caseSensitive:
                return self[0]
            else:
                return self[0].lower()+self[0].upper()+self[0]
        return closing




class Repeat(Rule):
    minCt = 0
    maxCt = None
    sepMayTerm = False  # is separator allowed as terminator?
    closingChars = ''
    separator = Epsilon()

    def parse(self, input, produce, startState):

        rule = self.rule
        state = startState
        data = []

        newState = input.parse(rule, data.append, state)

        if isinstance(newState,ParseError):
            if self.minCt>0:
                return newState  # it's an error
            else:
                return state  # non-error empty match

        ct = 1; maxCt = self.maxCt; state = newState
        while not input.finished(state) and (maxCt is None or ct<maxCt):

            newState = input.parse(self.sep, data.append, state)
            if isinstance(newState,ParseError):
                break   # no more items

            state = newState
            newState = input.parse(rule, data.append, state)
            if isinstance(newState,ParseError):
                if self.sepMayTerm:
                    break   # if sep can be term, it's okay to end here
                return newState  # otherwise pass the error up

            ct += 1
            state = newState

        produce(data)   # treat repeat as a list
        return state

    def format(self, data, write):

        if not data:
            return

        rule = self.rule

        for d in data[:-1]:
            rule.format(d,write)
            self.sep.format(d,write)

        rule.format(data[-1],write)


    def withTerminators(self,terminators,memo):

        key = id(self), terminators
        if key in memo:
            return memo[key][0]

        kw = self.__dict__.copy()
        if 'rule' in kw:
            del kw['rule']
        del kw['initArgs']

        kw['closingChars'] = uniquechars(terminators+self.closingChars)
        r = self.__class__(
            self.rule.withTerminators(kw['closingChars'],memo),
            **kw
        )
        memo[key] = r, self
        r._computeRule(memo)
        return r








    def _computeRule(self, memo=None):

        rule = self.rule = adapt(self.initArgs[0],IRule)

        closeAll = uniquechars(self.closingChars)

        if not memo:
            memo = { (id(self),closeAll): (self, self) }

        key = id(rule), closeAll

        if key in memo:
            rule = memo[key][0]
        else:
            rule = rule.withTerminators(closeAll, memo)
            memo[key] = rule, self

        return rule

    rule = Make(lambda self: self._computeRule(), attrName='rule')

    closingChars = ''

    def __init__(self, *__args, **__kw):
        if len(__args)<>1:
            return self.__init__(Sequence(*__args),**__kw)
        self.__dict__.update(__kw)
        self.initArgs = __args
        self.sep = adapt(self.separator, IRule)
        if 'closingChars' not in self.__dict__:
            self.closingChars = self.sep.getOpening('',{})

    def getOpening(self,closing,memo):
        if 'rule' not in self.__dict__:
            self.rule = self._computeRule(memo)
        return self.rule.getOpening(closing,memo)





















class Tuple(Sequence):

    """Sequence of unnamed values, rendered as a tuple (e.g. key/value)"""

    def parse(self, input, produce, startState):

        out = []
        state = input.parse(super(Tuple,self), out.append, startState)

        if isinstance(state,ParseError):
            return state

        produce( tuple(out) )
        return state


    def format(self, data, write):
        p = 0
        for rule in self.rules:
            rule.format(data[p],write)
            if not isinstance(rule,str):
                p+=1



















class MatchString(Rule):

    """Match a regex, or longest string that doesn't include a terminator"""

    output = ''
    openingChars = ''
    terminators = ''
    explicit_pattern = False

    def __init__(self,pattern=None,**kw):

        self.__dict__.update(kw)

        if pattern is None:
            self.explicit_pattern = False
            if self.terminators:
                pattern = '[^%s]*' % re.escape(
                    ''.join(dict([(t[:1],1) for t in self.terminators]))
                )
            else:
                pattern = '.+'

        else:
            self.explicit_pattern = True

        if isinstance(pattern,str):
            pattern = re.compile(pattern)

        self.pattern = pattern


    def withTerminators(self,terminators,memo):
        if terminators==self.terminators:
            return self
        d = self.__dict__.copy()
        if not self.explicit_pattern:
            del d['pattern']
        d['terminators'] = terminators
        return self.__class__(**d)


    def parse(self, inputStr, produce, startAt):
        m = self.pattern.match(inputStr, startAt)
        if not m:
            return ParseError(
                "Failed match for %r at position %d in %r" %
                (self.pattern.pattern, startAt, inputStr)
            )
        state = m.end()
        return state


    def getOpening(self,closing,memo):
        return self.openingChars


    def format(self,data,write):

        if self.pattern is None:
            write(data)
        elif self.output is not None:
            write(self.output)
        else:
            raise MissingData   # we don't know how to format!


    # Hash/compare based on pattern so that equivalent rules
    # will memoize the same

    def __hash__(self):
        return hash(self.pattern)

    def __cmp__(self,other):
        return cmp(self.pattern, other)








class ExtractString(Rule):

    """Return matched subrule as a string"""

    __slots__ = 'rule', 'terminators'

    def __init__(self, rule=MatchString(), terminators=''):
        self.rule = adapt(rule,IRule)
        self.terminators = terminators

    def parse(self, input, produce, startState):
        out = []
        state = input.parse(self.rule, out.append, startState)
        if isinstance(state,ParseError):
            return state

        produce(input[startState:state])
        return state


    def withTerminators(self,terminators,memo):
        if self.terminators==terminators:
            return self
        return self.__class__(
            self.rule.withTerminators(terminators,memo), terminators
        )

    def getOpening(self,closing,memo):
        return self.rule.getOpening(closing,memo)

    def format(self,data,write):
        write(data)









class Named(Rule):

    """Named value - converts to/from dictionary/items"""

    __slots__ = 'name', 'rule'

    def __init__(self, name, rule=ExtractString()):
        self.name = name
        self.rule = adapt(rule,IRule)

    def withTerminators(self,terminators,memo):
        return self.__class__(
            self.name, self.rule.withTerminators(terminators,memo)
        )

    def getOpening(self,closing,memo):
        return self.rule.getOpening(closing,memo)


    def parse(self, input, produce, startState):
        return self.rule.parse(
            input, lambda v: produce((self.name,v)), startState
        )

    def format(self, data, write):
        try:
            value = data[self.name]
        except KeyError:
            raise MissingData(self.name)
        return self.rule.format(value, write)











class Conversion(Rule):

    formatter = str
    converter = str
    canBeEmpty = False
    defaultValue = NOT_GIVEN


    def __init__(self, rule=ExtractString(), **kw):
        self.__dict__.update(kw)
        self.rule = adapt(rule, IRule)


    def parse(self, input, produce, startState):

        out = []
        state = input.parse(self.rule, out.append, startState)
        if isinstance(state,ParseError):
            return state

        out, = out
        if out=='' and self.canBeEmpty and self.defaultValue is not NOT_GIVEN:
            value = self.defaultValue
        else:
            value = self.converter(out)

        produce(value)
        return state


    def withTerminators(self, terminators,memo):

        kw = self.__dict__.copy()
        kw['rule'] = self.rule.withTerminators(terminators,memo)
        return self.__class__(**kw)


    def getOpening(self,closing,memo):
        return self.rule.getOpening(closing,memo)


    def format(self, data, write):

        if self.defaultValue is not NOT_GIVEN and data==self.defaultValue:
            if self.canBeEmpty:
                return
            else:
                raise MissingData

        value = self.formatter(data)
        if not value and not self.canBeEmpty:
            raise MissingData

        self.rule.format(value, write)




























class Alternatives(Rule):

    """Match one out of many alternatives"""

    __slots__ = 'alternatives'

    def __init__(self, *alternatives):
        self.alternatives = [adapt(a,IRule) for a in alternatives]

    def withTerminators(self,terminators,memo):
        return self.__class__(
            *tuple([a.withTerminators(terminators,memo) for a in self.alternatives])
        )

    def getOpening(self,closing,memo):
        return ''.join([a.getOpening('',memo) for a in self.alternatives])

    def parse(self, input, produce, startState):
        for rule in self.alternatives:
            state = input.parse(rule,produce,startState)
            if not isinstance(state,ParseError):
                return state
        else:
            return ParseError(
                "Parse error at position %d in %r" % (startState,input)
            )

    def format(self, data, write):
        for rule in self.alternatives:
            try:
                out = []
                rule.format(data,out.append)
            except MissingData:
                continue
            if out:
                map(write,out)
                return
        else:
            raise MissingData


class Set(Alternatives):

    def parse(self, input, produce, startState):

        rules = self.alternatives[:]
        state = startState

        while rules and not input.finished(state):
            for rule in rules:
                newPos = input.parse(rule,produce,state)
                if isinstance(newPos,ParseError):
                    continue
                else:
                    state = newPos    # XXX handle separator?
                    rules.remove(rule)
                    break
            else:
                return ParseError(
                    "No match found at position %d in %r" % (state,input)
                )

        return state

    def format(self, data, write):

        for rule in self.alternatives:
            try:
                out = []
                rule.format(data,out.append)
            except MissingData:
                continue
            if out:
                map(write,out)








    def withTerminators(self,terminators,memo):
        # make sure alternatives consider each other as possible terminators
        return super(Set,self).withTerminators(
            uniquechars(
                terminators+''.join(
                    [a.getOpening('',memo) for a in self.alternatives]
                )
            ), memo
        )
































class StringInput(Input, str):

    def startState(self):
        return 0

    def finished(self,state):
        return state>=len(self)



def parse(input, rule):

    out = []
    input = adapt(input,IInput)
    state = input.parse(rule, out.append, input.startState())

    if isinstance(state,ParseError):
        raise state

    if not input.finished(state):
        raise ParseError(
            "Expected EOF, found %r at position %d in %r" %
            (input[state:], state, input)
        )

    return dict(out)


def format(aDict, syntax):
    out = []
    syntax.format(aDict, out.append)
    return ''.join(out)









