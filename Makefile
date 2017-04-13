VIRTUALENV ?= ~/.virtualenv

default: clean test

all: $(TARGETS)

clean:
	-@echo y | pip uninstall data-migrator
	@rm -rf docs/_build
	@find . -name *.pyc -delete
	@rm -rf build data_migrator.egg* dist

.PHONY: test dist docs

test:
	@python -m unittest discover -s test

dist:
	@python setup.py bdist_wheel --universal

dev: ## install for development
	@pip install -e .

docs:
	cd docs && make html

virtualenv: $(VIRTUALENV)/dm/bin/activate
	virtualenv $(VIRTUALENV)/dm
