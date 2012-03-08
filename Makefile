all: clean

clean:
	rm -rf test_program.py coverdir
	find . -maxdepth 1 -type f -iname "*.pyc" ! -iname program.pyc -prune -exec rm {} +

.PHONY: clean
