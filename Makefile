VIRTUALENV ?= ~/.virtualenv
REPORTS ?= reports
DOCS ?= docs

default: clean test

all: $(TARGETS)

clean: ## Clean all build files
	-@echo y | pip uninstall data-migrator
	@rm -rf $(DOCS)/_build
	@rm -rf $(REPORTS)
	@find . -name *.pyc -delete
	@rm -rf build data_migrator.egg* dist
	-@rm -f .coverage

.PHONY: test dist docs version help

version: ## Show current version
	@python -c "import data_migrator; print(data_migrator.__version__)"

bandit: | $(REPORTS) ## Do bandit security check
	@bandit --ini ./.bandit -r ./src --format json -o $(REPORTS)/bandit.json

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

coverage: | $(REPORTS) ## Check test coverage
	coverage run -m unittest discover -s tests/
	coverage xml -o $(REPORTS)/coverage.xml
	python-codacy-coverage -r $(REPORTS)/coverage.xml

docs: ## Run documentation
	cd $(DOCS) && make html

virtualenv: $(VIRTUALENV)/dm/bin/activate
	virtualenv $(VIRTUALENV)/dm

upload: ## Upload latest release to pypi
	twine upload dist/*

drop:
	bumpversion drop --commit

$(REPORTS):
		mkdir -p $@

help: ## Shows help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""
