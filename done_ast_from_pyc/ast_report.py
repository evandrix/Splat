from collections import defaultdict
import traceback
import atexit
import linecache

loaded_modules = [ ]

class FileInfo(object):
    def __init__(self, filename, enter_linenos, reach_linenos):
        self.filename = filename
        self.enter_linenos = enter_linenos
        self.reach_linenos = reach_linenos
        self.ast_enter = defaultdict(int)
        self.ast_leave = defaultdict(int)
        self.ast_reach = defaultdict(int)

def register_module(filename, enter_linenos, reach_linenos):
    #print filename, enter_linenos, reach_linenos
    info = FileInfo(filename, enter_linenos, reach_linenos)
    loaded_modules.append(info)
    return info.ast_enter, info.ast_leave, info.ast_reach

def check_string(left, right, lineno, col_offset):
    if not isinstance(left, basestring):
        return left % right
    try:
        return left % right
    except Exception, err:
        print "Could not interpolate: %s" % (err,)
        traceback.print_stack()
        raise

# Basic coverage report
def report_coverage():
    for fileinfo in loaded_modules:
        # This will contain a list of all results as a 3-ple of
        #   lineno, col_offset, "text message"
        report = []
        # These should have both 'enter' and 'leave' counts.
        for id, (lineno, col_offset) in fileinfo.enter_linenos.items():
            if id not in fileinfo.ast_enter:
                report.append( (lineno, col_offset, "not entered") )
            elif id not in fileinfo.ast_leave:
                report.append( (lineno, col_offset, "enter %d but never left" %
                                fileinfo.ast_enter[id]) )
            else:
                delta = fileinfo.ast_leave[id] - fileinfo.ast_enter[id]
                report.append( (lineno, col_offset, "enter %d leave %d (diff %d)" %
                                (fileinfo.ast_enter[id], fileinfo.ast_leave[id], delta)) )

        # These only need to be 'reach'ed
        for id, (lineno, col_offset) in fileinfo.reach_linenos.items():
            if id not in fileinfo.ast_reach:
                report.append( (lineno, col_offset, "not reached") )
            else:
                report.append( (lineno, col_offset, "reach %d" % (fileinfo.ast_reach[id],)) )

        # sort by line number, breaking ties by column offset
        report.sort()

        print "Coverage results for file", fileinfo.filename
        for lineno, col_offset, msg in report:
            print "%d:%d %s" % (lineno, col_offset+1, msg)
            print linecache.getline(fileinfo.filename, lineno).rstrip()

# Dump the coverage results when Python exist.
atexit.register(report_coverage)
