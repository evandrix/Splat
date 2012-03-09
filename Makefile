all: clean

clean:
	rm -rf test_*.{py,json} coverdir
	find . -maxdepth 1 -type f -iname "*.pyc" ! -iname program.pyc ! -iname fizzbuzz.pyc ! -iname factorial.pyc ! -iname simple.pyc ! -iname "m*.pyc" -prune -exec rm {} +

.PHONY: clean
