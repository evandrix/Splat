"""Utility class for writing Python, XML, etc. w/easy indentation handling"""

class IndentedStream:

    """Adapter that adds indentation management to a write stream

        Basic Usage::

            >>> f = IndentedStream(sys.stdout)
            >>> f.write('{\n'); f.push(1); f.write('foo;\n'); f.pop(); \
                f.write('}\n');

        Outputs::

            {
                foo;
            }

        IndentedStreams have a indent level stack which keeps track of
        each new margin size; push sets a new margin (relative or absolute
        by spaces or tabs), and pop restores the last set margin.  Text written
        is split on line breaks and indented as needed.
    """

    tabwidth = 4
    maxdepth = 80
    needSpaces = 1
    spaces = ''

    def __init__(self,stream=None,tabwidth=4):

        """Create an indented stream from an existing stream"""

        if stream is None:
            from sys import stdout
            stream = stdout
        self.stream = stream
        self.tabwidth = tabwidth
        self.stack = [0]


    def setTabWidth(self,tabwidth):
        """Change current tab stop width"""
        self.tabwidth = tabwidth


    def setMargin(self,tabs=0,indent=0,outdent=0,absolute=None,absTabs=None):

        """Set current margin using relative or absolute spaces or tabs

            Examples::

                f=IndentedStream(sys.stdout,tabwidth=8)
                f.setMargin(1)           # indent by 8 spaces (current tab width)
                f.setMargin(-1)          # outdent by 8 spaces
                f.setMargin(indent=4)    # indent by 4 spaces (could outdent=-4)
                f.setMargin(outdent=4)   # outdent by 4 spaces (could indent=-4)
                f.setMargin(absolute=20) # set margin to 20 spaces
                f.setMargin(absTabs=3)   # set margin to 3 * current tab width

            Note that 'setMargin()' does not save the current margin; if you
            need it to be saved, use 'push()' instead, which will take the same
            arguments.
        """

        if absTabs is not None:
            absolute = absTabs * self.tabwidth

        if absolute is None:
            margin = self.stack[-1] + indent - outdent + tabs*self.tabwidth
        else:
            margin = absolute

        self.stack[-1] = max(min(margin,self.maxdepth),0)
        self._setspaces()







    def push(self,*args,**kw):
        """Save the current margin, and optionally set a new one

            This method optionally accepts all the same parameters as
            'setMargin()', so that you can save the current margin and set a new
            one all in one step.  If no arguments, just saves the current
            margin.
        """
        self.stack.append(self.stack[-1])
        if args or kw:
            apply(self.setMargin,args,kw)


    def pop(self):
        """Restore the most recently saved margin - underflow is ignored"""
        stack = self.stack
        if len(stack)>1:
            stack.pop()
            self._setspaces()


    def _indent(self):
        if self.needSpaces:
            self.stream.write(self.spaces)
            self.needSpaces=0


    def _setspaces(self):
        self.spaces = ' ' * self.stack[-1]


    def __getattr__(self,name):
        return getattr(self.stream,name)








    def write(self,data):

        """Write 'data' to stream, indenting as needed"""

        if '\n' in data:

            lines = data.split('\n')
            write = self.stream.write
            indent = self._indent

            for l in lines[:-1]:
                if l:
                    indent()
                    write(l)
                write('\n')
                self.needSpaces = 1

            if lines[-1]:
                indent()
                write(lines[-1])
        else:
            self._indent()
            self.stream.write(data)


















