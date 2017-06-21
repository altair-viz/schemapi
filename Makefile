all: install

install:
	python setup.py install

test:
	py.test altair_parser --doctest-modules

test-coverage:
	py.test altair_parser --cov=altair_parser
