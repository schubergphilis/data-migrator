VIRTUALENV ?= ~/.virtualenv

default: clean test

all: $(TARGETS)

clean:
	-@echo y | pip uninstall data-migrator
	@rm -rf docs/_build
	@find . -name *.pyc -delete
	@rm -rf build data_migrator.egg* dist
	@rm .coverage coverage.xml

.PHONY: test dist docs

test:
	@python -m unittest discover -s test

dist:
	@python setup.py sdist --formats=gztar,zip bdist_wheel

dev: ## install for development
	@pip install -e .
	@pip install -r py.requirements/build.txt

coverage:
	coverage run -m unittest discover -s test/
	coverage xml
	python-codacy-coverage -r coverage.xml

docs:
	cd docs && make html

virtualenv: $(VIRTUALENV)/dm/bin/activate
	virtualenv $(VIRTUALENV)/dm

register_test:
	python setup.py register -r pypitest

upload:
	python setup.py register -r pypi
	twine upload -s dist/data_migrator-0.4*
