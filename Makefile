all: run

run:
	python -m compileall lazy_test_src.py
	mv lazy_test_src.pyc lazy_test.pyc
	python introspection.py

clean:
	rm -rf *.pyc

.PHONY: clean
