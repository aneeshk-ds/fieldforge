PYTHON := .venv/bin/python
DBT := .venv/bin/dbt
export UV_CACHE_DIR := $(CURDIR)/.uv-cache
export UV_PYTHON_INSTALL_DIR := $(CURDIR)/.uv-python

.PHONY: setup pipeline dbt test all dashboard spark benchmark clean

setup:
	uv venv --python 3.13 .venv
	uv pip install --python $(PYTHON) -e '.[dev]'

pipeline:
	$(PYTHON) -m fieldforge.cli pipeline
	$(DBT) build --project-dir dbt --profiles-dir dbt
	$(PYTHON) -m fieldforge.cli export-gold
	$(PYTHON) -m fieldforge.cli reconcile

dbt:
	$(DBT) build --project-dir dbt --profiles-dir dbt

test:
	$(PYTHON) -m pytest
	$(PYTHON) -m fieldforge.cli dashboard-check

all: pipeline test

dashboard:
	.venv/bin/streamlit run dashboard/app.py

spark:
	.venv/bin/spark-submit spark/standardize_orders.py

benchmark:
	$(PYTHON) -m fieldforge.cli benchmark

clean:
	$(PYTHON) -m fieldforge.cli clean
