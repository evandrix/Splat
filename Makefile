all: clean

clean:
	rm -rf test_program.py coverdir
	find . -type f -iname "*.pyc" ! -iname program.pyc -prune -maxdepth 1 -exec rm {} +

.PHONY: clean
