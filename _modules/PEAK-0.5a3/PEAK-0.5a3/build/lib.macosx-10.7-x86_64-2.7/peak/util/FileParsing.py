"""Line-Oriented File Parsing Tools

    This module supplies functions for creating and using "lineInfo"
    streams, which are iterables of '(source,lineNo,line)' tuples. The
    'source' is an indicator of the line's origin (e.g. a filename),
    while 'lineNo' is its line number within that source.  'line' is
    the actual text of the line.  This data structure is simple, fast,
    and easy to use.

    This module was created because the standard library 'ConfigParser'
    makes a lot of assumptions about syntax that don't necessarily
    work with every config file. For example, it assumes directives
    are order-insensitive key-value pairs, which doesn't work well for
    systems like PEAK, which might prefer to process a stream of
    directives in the original sequence.

    So, this module uses a stream-processing approach that should provide
    a reusable foundation for other types of line-oriented text processing.
    The basic tools are the 'fromStream()', 'fromFile()', and 'fromString()'
    functions, which respectively take an iterable, a filename, or a string,
    and return an iterator that yields '(source,lineNo,line)' tuples.

    Once you have a stream to play with, you can then use some of the
    processors such as 'iterConfigSections()' and 'iterConfigSettings()',
    which return iterators yielding various kinds of configuration data
    (based on ConfigParser-like syntax rules).  Or, you can use the
    'AbstractConfigParser' class as a base class to create your own
    specialized parsers.
"""

from __future__ import generators

import re

__all__ = [
    'fromStream', 'fromFile', 'fromString',
    'iterConfigSections', 'iterConfigSettings', 'AbstractConfigParser',
]



def fromStream(stream, source=None):

    """Produce '(source,lineNo,line)' tuple stream from input lines

    Calling 'fromStream(stream,source)' returns an iterator which yields
    '(source,lineNo,line)' tuples for each line in 'stream'.

    'stream' must be a sequence, iterator, or iterable file-like object
    that yields text lines.  (Line ending characters are stripped
    from line ends.)

    'source' should be a short string (e.g. filename) or other useful
    identifier of where the lines came from."""

    lineNo = 1

    for line in stream:

        while line and line[-1] in '\r\n':
            line=line[:-1]

        yield source, lineNo, line
        lineNo += 1


















def fromFile(filename, mode='r'):

    """Produce '(source,lineNo,line)' tuple stream from input file

    This is the equivalent of 'fromStream(open(filename,mode), filename)'.
    That is, it returns a line-info iterator with a source of 'filename'
    and the lines from 'open(filename,mode).readlines()'."""

    return fromStream(open(filename,mode), filename)


def fromString(text, source='<string>'):

    """Produce '(source,lineNo,line)' tuple stream from input file

    This is the equivalent of 'fromStream(StringIO(text), source)'.
    That is, it returns a line-info iterator with the supplied
    source name (default is '"<string>"') and the lines from
    'StringIO(text).readlines()'."""

    from cStringIO import StringIO
    return fromStream(StringIO(text), source)



















# Section header is []-enclosed section name, followed by optional whitespace
# and '#' or ';'-prefixed comment.

SECTION_MATCH = re.compile(r"\s*\[([^]]+)\]\s*([#;].*)?$").match

# Setting line is setting name (alphanumeric characters and most punctuation
# other than '#', ';', ':', or '=', followed by ':' or '=' as a name/value
# delimiter, followed by the option value.  Whitespace may appear between
# parts.

SETTING_MATCH = re.compile(r"([][\w,(){}\-+*?!._]+)\s*([:=])\s*(.*)$").match


# Only full-line comments are supported; comments are lines beginning
# with ';', '#', or the word 'rem' (case-insensitive).  All-blank lines
# are also considered comments, if they appear before a setting line.

COMMENT_MATCH = re.compile(r"([#;].*|rem(\s.*)?|\s*)$", re.I).match























def iterConfigSections(lineSource):

    """'(section,lines,info)' tuples per .ini-like section in 'lineSource'

    This function is used to break up a configuration file (.ini or
    ConfigParser-style) into sections based on '[]'-enclosed section
    names.  It returns an iterator which yields '(section,lines,info)'
    tuples for each section in the file.  The first yielded 'section'
    will be 'None' if any lines appear before the first section heading;
    all others will be the string that was between the '[]'.

    'lines' is always a list of '(source,lineNo,line)' tuples, suitable
    for use by 'iterConfigSettings()' or other lineInfo stream processors.

    'info' is a '(source,lineNo,line)' tuple representing the line where
    the section header (if any) appeared."""

    section = None
    lines   = []
    info    = (None, 0, None)

    for source, lineNo, line in lineSource:

        sectinfo = SECTION_MATCH(line)

        if sectinfo:

            if section or lines:
                yield section, lines, info

            section = sectinfo.group(1).strip()
            lines   = []
            info    = (source,lineNo,line)

        else:
            lines.append( (source, lineNo, line) )

    if section or lines:
        yield section, lines, info


def iterConfigSettings(lineSource):

    """'(name,value,lineInfo)' tuples per .ini-like setting in 'lineSource'

    'name' and 'value' will be 'None' for any non-blank, non-comment line
    which does not appear to be a valid option.  Otherwise, they are the
    setting's name and value, respectively.

    'lineInfo' is a standard lineInfo-tuple of '(source,lineNo,line)' data,
    with the difference that continuation lines are concatenated to 'line'.
    This is so that if one needs to display an error message that shows the
    source of the parsed value, the full logical line is included, even though
    the first physical line number would be used to identify the error line.

    Continuation Lines

        RFC822-style line continuations are supported, with leading whitespace
        stripped from continuation lines, and '"\\n"' separating the lines in
        the returned value.  Unlike ConfigParser, no other interpretation of
        'name' or 'value' is done, so it's up to you to do any case-folding,
        conversions, etc.

    Comment and Whitespace (blank line) Processing

        Comment lines are lines which begin with a ';', '#', or the word
        'rem' (case-insensitive).  No leading whitespace is allowed, to
        prevent confusion with continuation lines.  Because setting values
        are not interpreted, comments embedded on the same line with a setting
        or indented in a continuation line are returned as part of the value
        text.  If you want to support embedded comments, it is up to you to
        parse them out of the value.

        Comment lines are completely ignored, so you *can* have a comment
        line inside a series of continuation lines, as long as it has no
        leading whitespace on the line.  Blank (empty or whitespace-only)
        lines within a series of continuation lines are considered part of
        the setting value, and are rendered as empty lines in the value.
        Blank lines which appear at the end of a setting value, or before
        the first setting in the input stream, are ignored.
    """

    name = None
    value = None

    for source, lineNo, line in lineSource:

        if name and (not line.strip() or line[0] in ' \t'):
            value = "%s\n%s" % (value, line.strip())
            lineInfo = lineInfo[0], lineInfo[1], lineInfo[2]+'\n'+line
            continue

        if COMMENT_MATCH(line):
            continue

        if name:

            while value.endswith('\n'):
                value=value[:-1]

            yield name, value, lineInfo


        name     = None
        lineInfo = source, lineNo, line
        optinfo  = SETTING_MATCH(line)

        if optinfo:
            name, delim, value = optinfo.groups()
        else:
            # Unrecognized setting format!
            yield None, None, lineInfo


    if name:

        while value.endswith('\n'):
            value=value[:-1]

        yield name, value, lineInfo



class AbstractConfigParser(object):

    """Abstract configuration file parser based on sections and settings

        The basic idea of this class is that you subclass it, supplying
        replacements for the 'get_handler()' and/or 'add_setting()' methods.
        If your format will handle all sections the same way, just override
        'add_setting()'.  If it will handle sections differently, override
        'get_handler()' to return an appropriate method for processing settings
        in that section.  If you want sections which aren't parsed as settings
        at all, you'll need to revise the 'add_section()' method to handle
        such sections differently.

        To use your class, you'll create an instance of the parser, then
        call its 'readFile()', 'readStream()' or 'readString()' methods to
        process configuration data from as many sources as you like.  What
        will happens when each setting is received, is of course up to your
        subclass to determine."""

    def readFile(self, filename, mode='r'):
        """Read file 'filename' into configuration"""
        self.parse(fromFile(filename, mode))

    def readStream(self, stream, source):
        """Read 'stream' into configuration"""
        self.parse(fromStream(stream, source))

    def readString(self, text, source='<string>'):
        """Read 'text' into configuration"""
        self.parse(fromString(text, source))

    def parse(self, lineSource):
        """Read lineInfo-stream 'lineSource' into configuration"""
        section = self.add_section
        for s,l,li in iterConfigSections(lineSource):
            section(s,l,li)





    def add_section(self, section, lines, lineInfo):

        """Add a section to configuration"""

        handler = self.get_handler(section, lines, lineInfo)
        self.process_settings(section, lines, handler)


    def process_settings(self, section, lines, handler):

        """Process a section's worth of settings using 'handler'"""

        for n,v,l in iterConfigSettings(lines):
            handler(section,n,v,l)


    def get_handler(self, section, lines, lineInfo):

        """Override this to choose setting handlers per section"""

        return self.add_setting


    def add_setting(self, section, name, value, lineInfo):

        """Override this to implement your standard processing for settings"""

        if section is None:
            pass    # setting in un-named section

        elif name is None:
            pass    # unrecognized format

        print "%s: %s = %r %r" % (section, name, value, lineInfo)







