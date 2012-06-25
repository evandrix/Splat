# Demo 1
# gather active variables + their possible types
# and which of the branches use input arguments
cd /Users/lwy08/Dropbox/FYP/fyp/fyp
python main.py absolute.pyc

# Demo 2a
# assuming type information already gathered
# testing for branch coverage using (random) range of values
cd /Users/lwy08/Downloads
python find_all_paths.py
nosetests -vsw .

# Demo 2b
cd /Users/lwy08/Dropbox/FYP/fyp/fyp
python gui.py