from peak.api import *
from model import Document, Table, Row, Cell
from bisect import insort

GREEN  = ' bgcolor="#CFFFCF"'
RED    = ' bgcolor="#FFCFCF"'
GREY   = ' bgcolor="#EFEFEF"'
YELLOW = ' bgcolor="#FFFFCF"'


def parseTags(text,tag,startAt,startBy,contentProcessor):

    pos = startAt
    items = []

    while pos < startBy:
        tagStart = text.find("<"+tag,pos)

        if tagStart<0 or tagStart>=startBy:
            break

        contentStart = text.find(">", tagStart)
        if contentStart<0:
            break

        firstClose = text.find("</"+tag, contentStart)
        if firstClose<0:
            firstClose = startBy

        pos, item = contentProcessor(
            tag=tagStart, content=contentStart+1, close=firstClose
        )
        items.append(item)

    return pos,items






def findText(text,startAt,endBy):

    """Find the longest plain-text run (not counting whitespace)"""

    s = e = endBy
    foundLen = 0

    while startAt<endBy:

        ts = text.find('<',startAt)
        if ts<0:
            ts=endBy

        textLen = len(text[startAt:ts].strip())
        if textLen>foundLen:
            s=startAt
            e=ts
            foundLen=textLen

        startAt = text.find('>',ts)
        if startAt<0:
            break

        startAt += 1

    return s,e















class HTMLDocument(storage.EntityDM):

    text = binding.Require("Text of the HTML document to be processed")

    lctext = binding.Make(lambda self: self.text.lower())

    output = binding.Require(
        "Output stream, as a stream factory", adaptTo=naming.IStreamFactory
    )

    useAC = False

    stream = binding.Make(
        lambda self: self.output.create('t',autocommit=self.useAC)
    )

    document = binding.Make(lambda self: self[Document])

    edits = binding.Make(list)

    def _ghost(self, oid, state=None):

        if oid is Document:
            return Document()

        kind,tag,content,close = oid
        return kind()


    def _load(self, oid, ob):

        if oid is Document:
            pos, items = parseTags(
                self.lctext, "table", 0, len(self.text), self.makeTable
            )
            return {'tables':items,'summary':{}}

        raise AssertionError("Can't load state for anything but Document")



    def _insertText(self,pos,text):
        insort(self.edits, (pos,pos,text))


    def _tagAdditions(self,cell):
        score = cell.score

        if score.right:
            return GREEN

        elif score.wrong:
            return RED

        elif score.ignored:
            return GREY

        elif score.exceptions:
            return YELLOW

        return ''


    def _bodyAdditions(self,cell):

        score = cell.score
        additions = ''

        if cell.annotation:
            additions += self.annotation(cell.annotation)

        if score.wrong:
            if hasattr(cell,'actual'):
                additions += self.actual(str(cell.actual))

        if score.exceptions:
            additions += self.exception(cell.exc_info)

        return additions



    def _cellAsText(self,cell):
        return '<td%s>%s%s</td>' % (
            self._tagAdditions(cell), self.escape(cell.text),
            self._bodyAdditions(cell)
        )

    def _rowAsText(self,row):
        return '<tr>%s</tr>' % ''.join(
            [self._cellAsText(cell) for cell in row.cells]
        )

    def _tableAsText(self,table):
        return '<table>%s</table>' % ''.join(
            [self._rowAsText(row) for row in table.rows]
        )

    def _save(self,ob):

        if ob._p_oid is Document:
            self._saveChildren(
                ob,0,0,len(self.text),ob.tables,self._tableAsText
            )
            return  # nothing to save

        kind,tag,content,close = ob._p_oid

        if kind is Cell:
            self._saveCell(ob,tag,content,close)
        elif kind is Row:
            self._saveChildren(ob,tag,content,close,ob.cells,self._cellAsText)
        elif kind is Table:
            self._saveChildren(ob,tag,content,close,ob.rows,self._rowAsText)
        else:
            raise AssertionError("Unexpected item type", ob)


    def _new(self,ob):
        return None  # leave oid as None, allow parent to save us



    def _saveCell(self,cell,tag,content,close):

        ts,te = findText(self.text,content,close)

        tagText = self._tagAdditions(cell)
        if tagText:
            self._insertText(content-1,tagText)

        if cell.text<>self.unescape(self.text[ts:te]).strip():
            insort(self.edits, (content,close,self.escape(cell.text)))

        bodyText = self._bodyAdditions(cell)
        if bodyText:
            self._insertText(te,bodyText)


    def _saveChildren(self,ob,tag,content,close,children,toText):
        toInsert = ''
        for item in children:
            if item._p_oid is None:
                toInsert += toText(item)
            elif toInsert:
                self._insertText(item._p_oid[1],toInsert)
                toInsert = ''
        if toInsert:
            self._insertText(close,toInsert)


    def flush(self,ob=None):
        self._delBinding('edits')
        super(HTMLDocument,self).flush()
        lastPos = 0
        for (s,e,t) in self.edits:
            self.stream.write(self.text[lastPos:s])
            self.stream.write(t)
            lastPos=e
        self.stream.write(self.text[lastPos:])




    def makeTable(self,tag,content,close):

        pos, rows = parseTags(
            self.lctext, "tr", content, close, self.makeRow
        )

        table = self.preloadState(
            (Table,tag,content,close),
            {'rows':rows, 'document':self.document}
        )

        for row in rows: row.__dict__['table'] = table
        return pos, table


    def makeRow(self,tag,content,close):

        pos, cells = parseTags(
            self.lctext, "td", content, close, self.makeCell
        )

        if not cells:
            pos, cells = parseTags(
                self.lctext, "th", content, close, self.makeCell
            )

        row = self.preloadState(
            (Row,tag,content,close),
            {'cells':cells, 'document':self.document}
        )

        for cell in cells: cell.__dict__['row'] = row
        return pos, row








    def makeCell(self,tag,content,close):

        pos, subTables = parseTags(
            self.lctext, "table", content, close, self.makeTable
        )

        ts,te = findText(self.text,content,close)

        return pos, self.preloadState(
            (Cell,tag,content,close),
            {'document':self.document,
             'text':self.unescape(self.text[ts:te]).strip()
            }
        )



























    def exception(exc_info):
        from traceback import format_exception
        return "<hr><pre><font size=-2>%s</font></pre>" % ''.join(
            format_exception(*exc_info)
        )
    exception = staticmethod(exception)


    def actual(klass,text):
        return "%s<hr>%s%s" % (
            klass.smallLabel("expected"), klass.escape(text),
            klass.smallLabel("actual")
        )
    actual = classmethod(actual)


    def smallLabel(text):
        return ' <font size="-1" color="#C08080"><i>%s</i></font>' % text
    smallLabel = staticmethod(smallLabel)


    def annotation(text):
        return ' <font color="#808080">%s</font>' % text
    annotation = staticmethod(annotation)


    def escape(text):
        return text.replace(
            '&','&amp;'
        ).replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
    escape = staticmethod(escape)


    def unescape(text):
        return text.replace(
            '&quot;','"'
        ).replace('&gt;','>').replace('&lt;','<'
        ).replace('&nbsp;',' ').replace('&amp;', '&')
    unescape = staticmethod(unescape)


