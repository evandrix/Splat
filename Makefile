all: run

run:
	python prototype.py

clean:
	rm -rf *.py{c,o,d,z}

.PHONY: clean
