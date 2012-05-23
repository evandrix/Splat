"""Name parsing and formatting tools"""

import re
from peak.api import exceptions


__all__ = [
    'UnspecifiedSyntax', 'PathSyntax', 'FlatSyntax',
]


class UnspecifiedSyntax(object):

    """Dummy (null) Syntax"""

    def parse(*args):
        raise NotImplementedError

    def format(*args):
        raise NotImplementedError





















class PathSyntax(object):

    """Name parser"""

    def __init__(self,

         direction=0,
         separator='',
         escape='',

         ignorecase=None,
         trimblanks=None,

         beginquote='',
         endquote='',
         beginquote2='',
         endquote2='',

         multi_quotes = False,
         decode_parts = True,

    ):

        self.multi_quotes = multi_quotes
        self.decode_parts = decode_parts
        self.direction    = direction
        self.separator    = separator

        if direction not in (-1,0,1):
            raise ValueError, "Direction must be 1, 0 (flat), or -1 (reverse)"

        if direction and not separator:
            raise ValueError, "Separator required for hierarchical syntax"

        if separator and not direction:
            raise ValueError, "Separator not meaningful for flat syntax"

        if endquote and not beginquote:
            raise ValueError, "End quote supplied without begin quote"


        if endquote2 and not beginquote2:
            raise ValueError, "End quote 2 supplied without begin quote 2"

        if beginquote2 and not beginquote:
            raise ValueError, "Begin quote 2 supplied without begin quote 1"

        endquote = endquote or beginquote
        endquote2 = endquote2 or beginquote2

        quotes = beginquote,endquote,beginquote2,endquote2
        quotes = dict(zip(quotes,quotes)).keys()    # unique strings only

        self.metachars = filter(None,[escape] + quotes)

        if escape and quotes:
            self.escapeFunc = re.compile(
                "(" + '|'.join(
                    map(re.escape,
                        filter(None,self.metachars+[separator])
                    )
                ) + ")"
            ).sub
            self.escapeTo = re.escape(escape)+'\\1'

        self.escape = escape
        self.trimblanks = trimblanks
        self.ignorecase = ignorecase

        if beginquote2:
            self.quotes = (beginquote,endquote), (beginquote2,endquote2)
        elif beginquote:
            self.quotes = (beginquote,endquote),
        else:
            self.quotes = ()

        if escape:
            escapedChar = re.escape(escape)+'.|'
        else:
            escapedChar = ''


        quotedStrs = ''
        bqchars = ''

        for bq,eq in self.quotes:
            bq_ = re.escape(bq[:1])
            eq_ = re.escape(eq[:1])
            bq = re.escape(bq)
            eq = re.escape(eq)
            quotedStrs += \
                "%(bq)s(?:%(escapedChar)s[^%(eq_)s])*%(eq)s|" % locals()
            bqchars += bq_

        if separator:
            sep         = re.escape(separator)
            optionalSep = "(?:%s)?" % sep
            sepOrEof    = "(?:%s)|$" % sep
        else:
            sep, optionalSep, sepOrEof = '', '', '$'

        if sep or bqchars:
            charpat = "[^%s%s]" % (sep,bqchars)
        else:
            charpat = '.'

        if multi_quotes:
            content = "( (?: %(quotedStrs)s %(escapedChar)s %(charpat)s )* )"
        else:
            content = "( %(quotedStrs)s (?:%(escapedChar)s%(charpat)s)*    )"

        content = content % locals()
        PS = """
            %(optionalSep)s
            %(content)s         # Contents in the middle
            (?=%(sepOrEof)s)    # separator or EOF last
        """ % locals()

        self.parseRe = re.compile(PS,re.X)

        if escape:
            self.unescape = re.compile(re.escape(escape)+'(.)').sub

    def format(self, seq):

        """Format a sequence as a string in this syntax"""

        if self.escape and self.decode_parts:
            n = [self.escapeFunc(self.escapeTo,part) for part in seq]
        else:
            n = [part for part in seq]

        if not filter(None,n):
            n.append('')

        if self.direction<0:
            n.reverse()

        return self.separator.join(n)

























    def parse(self, aStr):

        """Parse a string according to defined syntax"""

        startStr = aStr

        sep = self.separator

        for m in self.metachars:
            if aStr.find(m)>=0: break

        else:

            if sep:
                n = aStr.split(sep)
                if self.trimblanks:
                    n=[s.strip() for s in n]
                if not filter(None,n): n.pop()
                if self.direction<0:
                    n.reverse()
                return n

            else:
                return [aStr]

        n = []
        ps = self.parseRe
        quotes = self.quotes
        escape = self.escape
        unescape = self.unescape
        tb = self.trimblanks
        do_unescape = self.decode_parts and escape
        use_quotes  = self.decode_parts and quotes and not self.multi_quotes

        if aStr.startswith(sep):
            n.append('')
            aStr=aStr[len(sep):]




        while aStr:
            m = ps.match(aStr)

            if m:
                s = m.group(1)  # get the content of the path segment

                if use_quotes:
                    for bq,eq in quotes:
                        if s.startswith(bq):
                            # strip off surrounding quotes
                            s=s[len(bq):-len(eq)]
                            break

                if do_unescape and escape in s:
                    # unescape escaped characters
                    s = unescape('\\1',s)

                if tb:
                    s = s.strip()

                n.append(s)
                aStr = aStr[m.end():]

            else:
                raise exceptions.InvalidName(startStr)

        if self.direction<0:
            n.reverse()

        return n


FlatSyntax = PathSyntax()








