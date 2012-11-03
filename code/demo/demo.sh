# Demo 1
# figure out shape of function input arguments
cd /Users/lwy08/Dropbox/FYP/fyp/fyp; python main.py trivial
cd trivial-tests; nosetests; cd ..

# Demo 2a
# test for branch coverage using (random) range of values
# open absolute.py
cd /Users/lwy08/Dropbox/FYP/fyp/fyp; python all_paths.py absolute.pyc
# open test_absolute.py
python test_absolute.py

# Demo 2b
# graphic visualisation script
cd /Users/lwy08/Dropbox/FYP/fyp/fyp; python gui.py