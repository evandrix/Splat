#
# Add line numbers to a source file and display in a browser
# file_line_numbers.py
# Author: S.Prasanna
#

import sys
import traceback
import tempfile
import os

#Default browsers for Windows and UNIX, change as needed
BROWSER_WIN="C:\Program Files\Internet Explorer\iexplore"
BROWSER_UNIX="/usr/bin/firefox"

def add_line_number(infile):
    """ Prints a source file with line numbers in a browser. """

    try:
        fin = open(infile, "r")        
    except:
        print "An exception occured in opening the input file."
        traceback.print_exc()
        return 1

    outfilename = "%s.html" % infile #tempfile.mkstemp()[1]

    try:
        fout = open(outfilename, "w")
    except:
        print "An exception occured in opening the output file."
        traceback.print_exc()
        return 1

    total_lines = sum(1 for line in fin)
    total_digits = len(str(total_lines))
   
    fin.seek(0)

    lines_written = 1
    
    for lines in fin:
        fout.write(repr((str(lines_written) + ".")).ljust(total_digits + 4).replace("'", "") + lines)
        lines_written = lines_written + 1

    fin.close()
    fout.close()

    print "Printing the line numbers of the input file in a browser."
    print "Close the browser to exit."

    if os.name == "nt":
        return os.system("\"" + BROWSER_WIN + "\" " + outfilename)
    else:
        return os.system("\"" + BROWSER_UNIX + "\" " + outfilename)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: file_line_number.py <file-name>"
        sys.exit(1)

    input_file = sys.argv[1]
    add_line_number(input_file)
