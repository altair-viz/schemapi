all: install

install:
	python setup.py install

test:
	py.test jsonschema_apigen --doctest-modules

test-coverage:
	py.test jsonschema_apigen --cov=jsonschema_apigen
