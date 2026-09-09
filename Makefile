PYTHON := .venv/bin/python
DBT := .venv/bin/dbt
BENCHMARK_PROFILE ?= 10x
BENCHMARK_CUSTOMERS ?= 5000
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
	FIELDFORGE_DATA_ROOT="$(CURDIR)/data/benchmarks/$(BENCHMARK_PROFILE)" \
	FIELDFORGE_ARTIFACTS_ROOT="$(CURDIR)/artifacts/benchmarks/$(BENCHMARK_PROFILE)" \
	$(PYTHON) -m fieldforge.cli benchmark --profile "$(BENCHMARK_PROFILE)" \
		--customers "$(BENCHMARK_CUSTOMERS)"

clean:
	$(PYTHON) -m fieldforge.cli clean
