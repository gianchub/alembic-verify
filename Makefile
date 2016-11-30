.PHONY: test

test: flake8 pylint pytest

pylint:
	pylint alembicverify -E

flake8:
	flake8 alembicverify test

pytest:
	coverage run --source=alembicverify --branch -m pytest test $(ARGS)
	coverage report --show-missing --fail-under=100
