python-packages := tests

all: check test

check: check_black check_isort check_flake8 check_pylint check_mypy check_contracts

check_black:
	black -l 100 --check $(python-packages)

check_isort:
	isort -rc -df -c $(python-packages)

check_flake8:
	flake8 $(python-packages)

check_pylint:
	pylint $(python-packages)

check_mypy:
	#mypy --pretty $(python-packages)

check_contracts:
	pyicontract-lint $(python-packages)

format:
	black -l 100 $(python-packages)
	isort -rc $(python-packages)

test: test_python

test_python:
	python3 -m pytest -n$(shell nproc) -vv -m "not hypothesis"

