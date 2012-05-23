"""A variety of ways to render the data from a cursor to a file object"""

from peak.api import *

class AbstractCursorFormatter(binding.Component):
    cursor = binding.Obtain('..')
    header = True
    footer = True
    delim  = '|'
    null   = 'NULL'

    def __call__(self, stdout):
        c = self.cursor
        
        if c._cursor.description is not None:
            self.formatSet(c, stdout)

        while c.nextset():
            if not c._cursor.description:
                continue

            self.betweenSets(stdout)
            self.formatSet(c, stdout)


    def betweenSets(self, stdout):
        print >>stdout


    def printFooter(self, c, stdout, nr):
        print >>stdout, "(%d rows)" % nr


    def formatSet(self, c, stdout):
        nrows = self.formatRows(c, stdout)

        if self.footer:
            self.printFooter(c, stdout, nrows)


    def toStr(self, val, width=None):
        if type(val) is unicode:
            val = val.encode('utf8')

        if val is None:
            if width is None:
                return self.null
            return self.null.ljust(width)[:width]
        elif width is None:
            return str(val)
        elif type(val) in (int, long):
            return "%*d" % (width, val)
        elif type(val) is float:
            return "%*g" % (width, val)
        else:
            return str(val).ljust(width)[:width]
        

class cursorToHoriz(AbstractCursorFormatter):
    def formatRows(self, c, stdout):
        out = stdout.write
        t, d, l = [], [], []
        first = 1
        nr = 0

        for r in c._cursor.description:
            w = r[2]
            if not w or w <= 0: w = r[3]
            if not w or w <= 0: w = 20 # XXX
            if w<len(r[0]): w = len(r[0])

            t.append(self.toStr(r[0], w)); d.append('-' * w); l.append(w)

        if self.header:
            out(' '.join(t)); out('\n')
            out(' '.join(d)); out('\n')
        
        for r in c:
            nr += 1
            i = 0
            o = []
            for v in r:
                o.append(self.toStr(v, l[i]))
                i += 1

            out(' '.join(o))
            out('\n')

        return nr


class cursorToVert(AbstractCursorFormatter):
    def formatRows(self, c, stdout):
        h = [x[0] for x in c._cursor.description]
        w = max([len(x) for x in h])
        nr = 0

        for r in c:
            i = 0
            nr += 1
            for v in r:
                print >>stdout, "%s %s" % (h[i].rjust(w), self.toStr(v))
                i += 1
            print >>stdout

        return nr


class cursorToPlain(AbstractCursorFormatter):
    def formatRows(self, c, stdout):
        d = self.delim
        nr = 0

        if self.header:
            print >>stdout, d.join([x[0] for x in c._cursor.description])

        for r in c:
            nr += 1
            print >>stdout, d.join([self.toStr(v) for v in r])

        return nr



class cursorToRepr(AbstractCursorFormatter):
    def formatRows(self, c, stdout):
        nr = 0

        if self.header:
            print >>stdout, `c._cursor.description`
        for r in c:
            nr += 1
            print >>stdout, `r`

        return nr



class cursorToLDIF(AbstractCursorFormatter):
    header = False
    footer = False

    def formatRows(self, c, stdout):
        nr = 0
        
        for r in c:
            nr += 1
            cols = r.keys()

            # dn must come first, according to RFC2849...
            try:
                dnix = cols.index('dn')
                del cols[dnix]
                cols.insert(0, 'dn')
            except ValueError:
                # ...though we can't be fully compliant if there is no dn!
                pass
                 
            for col in cols:
                vals = r[col]
                if type(vals) is not list:
                    vals = [vals]
                
                for val in vals:
                    if val is None:
                        continue
                        
                    val = self.toStr(val)
                    colname = "%s: " % col

                    ascii = True
                    for ch in val:
                        o = ord(ch)
                        if o < 32 or o > 126:
                            ascii = False
                            break

                    if not ascii:
                        colname = "%s:: " % col
                        val = ''.join(val.encode('base64').split())
                    
                    fl = 77 - len(colname)
                    stdout.write(colname + val[:fl] + '\n')
                    
                    val = val[fl:]
                    while val:
                        stdout.write(' ' + val[:76] + '\n')
                        val = val[76:]
                
            print >>stdout

        return nr


class cursorToCopy(AbstractCursorFormatter):
    """PostgreSQL/SQLite "COPY FROM" compatible format"""
    
    delim  = '\t'
    null   = '\\N'
    footer = False
   
    _map = {
        '\\' : '\\\\',  '\b' : '\\b',   '\f' : '\\f',
        '\n' : '\\n',   '\r' : '\\r',   '\t' : '\\t',   '\v' : '\\v'
    }
            
    def formatRows(self, c, stdout):
        nr = 0
        for r in c:
            print >>stdout, self.delim.join([self.toStr(v) for v in r])
            nr += 1

        return nr

    def toStr(self, v):
        if v is None:
            return self.null
        elif type(v) is unicode:
            v = v.encode('utf8')
        elif type(v) is not str:
            v = str(v)

        # XXX replace below with .encode('string_escape') in python 2.3?
        # XXX but, it does \x not \nnn escapes...

        nv = []
        
        for ch in v:
            o = ord(ch)
            m = self._map.get(ch)
            if m is not None:
                nv.append(m)
            elif o < 32 or o > 126:
                nv.append('\\%3o' % o)
            else:
                nv.append(ch)

        return ''.join(nv)


class cursorToCSV(AbstractCursorFormatter):
    csv = binding.Obtain('import:csv')
    dialect = 'excel'
    footer  = False
    delim   = None
    null    = None

    def formatRows(self, c, stdout):
        nr = 0

        kw = {
            'dialect' : self.dialect,
            'lineterminator' : '\n'
        }
        
        if self.delim is not None:
            kw['delimiter'] = self.delim
        
        wr = self.csv.writer(stdout, **kw)
        
        if self.header:
            wr.writerow([x[0] for x in c._cursor.description])

        for r in c:
            nr += 1
            wr.writerow([self.toStr(v) for v in r])
            
        return nr


class cursorToHTML(AbstractCursorFormatter):
    title = None

    def formatRows(self, c, stdout):
        nr = 0

        print >>stdout, "<table border>"

        if self.header:
            if self.title is not None:
                print >>stdout, "<tr><th colspan=%d>%s</th></tr>" % (
                    len(c._cursor.description), self.title
                )

            print >>stdout, "<tr>"

            for r in c._cursor.description:
                print >>stdout, "    <th>%s</th>" % self.htmlquote(
                    str(r[0])
                )
                
            print >>stdout, "</tr>"

        for r in c:
            nr += 1
            print >>stdout, "<tr>"
            for v in r:
                print >>stdout, "    <td align=left>%s</td>" % self.htmlquote(
                    self.toStr(v)
                )
            print >>stdout, "</tr>"

        print >>stdout, "</table>"

        return nr

    def printFooter(self, c, stdout, nr):
        print >>stdout, "\n<p>\n    (%d rows)\n</p>" % nr

    def toStr(self, v):
        if v is None:
            return self.null
        elif isinstance(v,unicode):
            return v.encode('utf8')
        elif not isinstance(v,str):
            return str(v)
        return v

    def htmlquote(self,v):
        v = v.replace('&','&amp;').replace('"','&quot;')
        return v.replace('<','&lt;').replace('>','&gt;')


class cursorToDDT(cursorToHTML):

    def toStr(self, v):
        return  `v`
