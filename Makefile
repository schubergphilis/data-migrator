VIRTUALENV ?= ~/.virtualenv

default: clean test

all: $(TARGETS)

clean:
	-@echo y | pip uninstall data-migrator
	@rm -rf docs/_build
	@rm -rf reports
	@find . -name *.pyc -delete
	@rm -rf build data_migrator.egg* dist
	-@rm -f .coverage coverage.xml

.PHONY: test dist docs version

version:
	@python -c "import data_migrator; print(data_migrator.__version__)"

test:
	@python -m unittest discover -s tests

dist:
	@python setup.py sdist --formats=gztar,zip bdist_wheel

dev: ## install for development
	@pip install -e .

dev_requirements:
	@pip install -r py.requirements/build.txt

dev_env:
	@pip install -r py.requirements/docs.txt
	@pip install -r py.requirements/build.txt
	@pip install -r py.requirements/environment.txt

tox:
	tox -e py27,py36,docs

coverage: dev
	coverage run -m unittest discover -s tests/
	coverage xml
	python-codacy-coverage -r coverage.xml

docs:
	cd docs && make html

virtualenv: $(VIRTUALENV)/dm/bin/activate
	virtualenv $(VIRTUALENV)/dm

register_test:
	python setup.py register -r pypitest

upload:
	# python setup.py register -r pypi
	# twine upload -s dist/data_migrator-0.4*
	for i in dist/*; do twine register $$i; done
	twine upload dist/*

drop:
	bumpversion drop --commit
