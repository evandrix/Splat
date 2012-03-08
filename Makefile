all: clean

clean:
	rm -rf test_program.py coverdir
	find . -maxdepth 1 -prune -type f -iname "*.pyc" ! -iname program.pyc -exec rm {} +

.PHONY: clean
