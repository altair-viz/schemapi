all: install

install:
	python setup.py install

test:
	py.test schemapi --doctest-modules

test-coverage:
	py.test schemapi --cov=schemapi
