VIRTUALENV ?= ~/.virtualenv

default: clean test

all: $(TARGETS)

clean: ## Clean all build files
	-@echo y | pip uninstall data-migrator
	@rm -rf docs/_build
	@rm -rf reports
	@find . -name *.pyc -delete
	@rm -rf build data_migrator.egg* dist
	-@rm -f .coverage coverage.xml

.PHONY: test dist docs version help

version: ## Show current version
	@python -c "import data_migrator; print(data_migrator.__version__)"

bandit:
	@bandit --ini ./.bandit -r ./src

test: ## Run all tests
	@python -m unittest discover -s tests

dist: ## Create a distribution
	@python setup.py sdist --formats=gztar bdist_wheel

dev: ## Install this package for development
	@pip install -e .

dev_requirements: ## Install dev environment requirements
	@pip install -r py.requirements/build.txt

dev_env: ## Install the dev env
	@pip install -r py.requirements/docs.txt
	@pip install -r py.requirements/build.txt
	@pip install -r py.requirements/environment.txt

tox: ## Run tox
	tox -e py27,py36,docs

coverage: dev ## Check test coverage
	coverage run -m unittest discover -s tests/
	coverage xml
	python-codacy-coverage -r coverage.xml

docs: ## Run documentation
	cd docs && make html

virtualenv: $(VIRTUALENV)/dm/bin/activate
	virtualenv $(VIRTUALENV)/dm

upload: ## Upload latest release to pypi
	twine upload dist/*

drop:
	bumpversion drop --commit


help: ## Shows help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""
