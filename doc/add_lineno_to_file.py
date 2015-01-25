#
# Add line numbers to a source file and display in a browser
#
import sys
import traceback
import tempfile
import os
#Default browsers for Windows and UNIX, change as needed
BROWSER_WIN="C:\Program Files\Internet Explorer\iexplore"
BROWSER_UNIX="/usr/bin/firefox"
BROWSER_MAC="/Applications/Firefox.app/Contents/MacOS/firefox"
def add_line_number(infile):
    """ Prints a source file with line numbers in a browser. """
    try:
        fin = open(infile, "r")
    except Exception as e:
        print "An exception occured in opening the input file."
        traceback.print_exc()
        return 1
    outfilename = "%s.html" % infile #tempfile.mkstemp()[1]
    try:
        fout = open(outfilename, "w")
    except Exception as e:
        print "An exception occured in opening the output file."
        traceback.print_exc()
        return 1
    total_lines  = sum(1 for line in fin)
    total_digits = len(str(total_lines))
    fin.seek(0)
    lines_written = 1
    print >> fout, "<pre>"
    for line in fin:
        fout.write(repr((str(lines_written) + ".")).ljust(total_digits + 4).replace("'", "") + line)
        lines_written += 1
    print >> fout, "\n</pre>"
    fin.close()
    fout.close()
    print "Printing the line numbers of the input file in a browser."
    if sys.platform == "darwin":
        return os.system("\"" + BROWSER_MAC + "\" " + outfilename)
    elif os.name == "linux2":
        return os.system("\"" + BROWSER_UNIX + "\" " + outfilename)
    else:
        return os.system("\"" + BROWSER_WIN + "\" " + outfilename)
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: file_line_number.py <file-name>"
        sys.exit(1)
    input_file = sys.argv[1]
    add_line_number(input_file)
