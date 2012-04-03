"""Readline configuration stack, with fallback if no readline module"""

import os

__all__ = ['pushRLHistory', 'popRLHistory', 'addRLHistoryLine']

try:
    import readline
    def_delims = readline.get_completer_delims()
    try:
        import rlcompleter
        readline.parse_and_bind("tab: complete")
        pycomplete = rlcompleter.Completer().complete
    except:
        pycomplete = None
except:
    readline = None

try:
    from readline import clear_history
except ImportError:
    def clear_history(): pass

try:
    from readline import get_current_history_length
except ImportError:
    def get_current_history_length(): pass














histstack = []
curhist = curcompl = curdelims = None
curlines = -1
_lastsize = 0

def _openHistory():
    # Make readline module's state match our current values
    try:
        readline.read_history_file(curhist)
    except:
        pass
    readline.set_completer(curcompl)
    readline.set_completer_delims(curdelims)
    readline.set_history_length(curlines)


def _closeHistory():
    # Ensure that our current history is written, and, if possible,
    # clear the history afterward.  Also, if possible, don't write
    # out any history content that might have come from a different
    # history.

    global _lastsize

    curlines = readline.get_history_length()
    currentsize = get_current_history_length()

    if currentsize is not None:
        lines_added = currentsize - _lastsize
        if lines_added<0:
            lines_added = currentsize
        if curlines==-1 or lines_added<curlines:
            readline.set_history_length(lines_added)

    readline.write_history_file(curhist)
    readline.set_history_length(curlines)

    clear_history()
    _lastsize = get_current_history_length()


def pushRLHistory(fn, completer=None, delims=None, environ=None, lines=-1):

    """Set up readline with given parameters, saving old state.
    This function is safe to call if readline is absent; it will
    silently do nothing.

    fn is a filename, relative to the home directory, for the history file.

    completer is a completion callable (see readline module documentation),
    or as a convenience, True may be passed for an interactive Python
    completer.

    delimns is a string containing characters that delimit completion words.
    passing None will use teh default set.

    environ is the environment in which to look up variables such as the
    home directory.

    lines is the number of lines of history to keep, or -1 for unlimited.
    """

    global curhist, curcompl, curdelims, curlines, histstack

    if readline:
        if environ is None:
            environ = os.environ

        if curhist:
            _closeHistory()
            histstack.append((curhist, curcompl, curdelims, curlines))

        homedir = environ.get('HOME', os.getcwd())
        curhist = os.path.join(homedir, fn)

        if completer is True:
            completer = pycomplete
        if delims is None:
            delims = def_delims



        curcompl = completer
        curdelims = delims
        curlines = lines

        _openHistory()


def popRLHistory():

    global curhist, curcompl, curdelims, curlines, histstack

    if readline:
        _closeHistory()

        if histstack:
            curhist, curcompl, curdelims, curlines = histstack.pop()
            _openHistory()


def addRLHistoryLine(l):
    if readline is not None:
        readline.add_history(l)



















