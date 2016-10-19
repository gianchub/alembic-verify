.PHONY: test

HTMLCOV_DIR ?= htmlcov

test: flake8 test_lib

flake8:
	flake8 alembicverify test

test_lib:
	coverage run --source=alembicverify -m pytest test $(ARGS)

coverage-html: test
	coverage html -d $(HTMLCOV_DIR)

coverage-report: test
	coverage report -m

coverage: coverage-html coverage-report test
