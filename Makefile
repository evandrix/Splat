all: run

run:
	python -m compileall lazy_test_src.py
	mv lazy_test_src.pyc lazy_test.pyc
	python introspection.py

install:
	virtualenv pyrulan
	source pyrulan/bin/activate
	workon pyrulan
	pip install -r requirements.txt

clean:
	rm -rf *.pyc

.PHONY: clean
