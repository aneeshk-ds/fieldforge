# Interview-grade tool practice plan

This file is the learning contract for FieldForge. It separates a working agent-built portfolio project from skills Aneesh has personally demonstrated. No arithmetic answer, dashboard preference, observation, or approval counts as tool mastery.

Learning is currently paused at Aneesh's instruction even though the delivery pipeline is complete. When Aneesh asks to resume, practice proceeds one bounded tool exercise at a time. The existing SQL Lab may be used when it genuinely supports the exercise, but it is not itself evidence that a tool was learned.

## Grading standard

A tool is **interview-gradable** only when one retained exercise contains all of the following:

1. **Explain:** Aneesh states the tool's role, input, output, and why it fits the task.
2. **Use:** Aneesh authors the material command, query, test, code, or configuration on real FieldForge data without being shown the finished answer.
3. **Diagnose:** Aneesh interprets output or fixes one realistic failure using evidence.
4. **Defend:** Aneesh answers one tradeoff or design-choice question.
5. **Retain:** Aneesh passes a later cold recheck of the central skill.

Every completed exercise must preserve the prompt, learner attempt, feedback, final artifact, command output, and these exact attribution labels:

- **Aneesh did**
- **Agent implemented**
- **Verification**

Current status for every row below is **not yet graded**. Prior KPI arithmetic and display-selection checkpoints are business-definition decisions, not tool practice.

## Complete project tool inventory

| # | Tool or format | FieldForge use | Interview-gradable practical |
|---:|---|---|---|
| 1 | Shell / terminal | Run, inspect, compose, and troubleshoot local pipeline commands and processes | Navigate the repository, inspect a failed run, use pipes/environment variables safely, and explain exit status and process ownership |
| 2 | Git | Version, diff, branch, and preserve verified milestones | Inspect a dirty branch, create a focused commit, explain staged vs unstaged state, and recover safely without destructive reset |
| 3 | GitHub and GitHub CLI | Synchronize the private branch and inspect hosted runs/artifacts | Prove local/remote SHA agreement, diagnose a failed run with `gh`, and explain branch/review boundaries |
| 4 | GitHub Actions | Execute the Linux quality gate and retain evidence | Read and modify a workflow, explain triggers/cache/artifacts, and diagnose a failing job from logs |
| 5 | Python 3.13 | Generate data, orchestrate stages, validate records, export evidence, and run independent controls | Implement one bounded pipeline/control change, test it, explain types/error handling, and debug a planted defect |
| 6 | Python packaging: `pyproject.toml` and Hatchling | Declare package metadata, supported Python, dependencies, extras, and build backend | Add or classify a dependency correctly, build/install the package, and explain runtime vs optional/dev dependencies |
| 7 | uv and `uv.lock` | Create the environment and reproduce exact dependencies | Rebuild from the lock, diagnose lock drift, and explain locked sync, cache, and Python selection |
| 8 | Make | Encode the supported command graph | Add or repair a target, explain prerequisites/environment propagation, and prove the target is reproducible |
| 9 | NumPy | Seed deterministic numeric generation | Produce and verify deterministic output, explain RNG state, and diagnose an accidental nondeterministic path |
| 10 | Faker | Generate reproducible synthetic identities and business records | Add a seeded field/provider, prove repeatability, and explain why synthetic data does not validate production realism |
| 11 | pandas | Profile, standardize, join, validate, and partition source records | Transform a real extract at declared grain, diagnose a dtype/join/null issue, and defend vectorized vs row-wise logic |
| 12 | PyArrow | Write/read typed stage artifacts and independent reconciliation inputs | Define or inspect a schema, round-trip data, diagnose a type mismatch, and explain Arrow's role between pandas and Parquet |
| 13 | Parquet | Store typed bronze, silver, quarantine, gold, and Spark outputs | Inspect schema/row groups, query selected columns, diagnose schema drift, and compare Parquet with CSV |
| 14 | CSV | Represent the six raw source extracts | Validate parsing and row counts, diagnose quoting/type ambiguity, and explain why CSV remains a source boundary rather than the analytical store |
| 15 | JSON | Store manifests, profiles, validation, reconciliation, Spark, and benchmark receipts | Read/write and validate one receipt, diagnose malformed or incomplete evidence, and explain machine-readable audit value |
| 16 | YAML | Declare dbt, CI, Compose, source, KPI, and planted-error configuration | Modify and validate one real contract, diagnose indentation/type mistakes, and explain declarative configuration tradeoffs |
| 17 | TOML | Declare Python packaging and local SQL Lab metadata | Make a safe manifest change, parse/validate it, and contrast TOML with YAML in this repository |
| 18 | SQL | Express staging, dimensions, facts, marts, tests, and investigation queries | Author a query with joins/CTEs/windows at a stated grain, diagnose duplication or null semantics, and explain the execution result |
| 19 | DuckDB | Query Parquet and host the local analytical warehouse | Build and inspect a table/query plan, diagnose a grain or file-lock problem, and defend DuckDB for this bounded local workload |
| 20 | dbt Core | Compile/run models, lineage, schema tests, singular tests, and documentation contracts | Add a model plus tests, inspect compiled SQL/lineage, diagnose a failing test, and explain `ref`, `source`, materialization, and grain |
| 21 | dbt-duckdb | Connect dbt semantics to the local DuckDB target | Configure and run an isolated target, diagnose path/profile behavior, and explain adapter responsibility |
| 22 | Jinja in dbt | Resolve `ref`/`source` and reusable compile-time SQL expressions | Trace rendered SQL, make one bounded templated change, diagnose compilation vs execution errors, and explain where templating should stop |
| 23 | Pandera | Declared dataframe-validation dependency | Implement one justified schema at a real stage boundary, test a failure, and compare it with the existing explicit validation logic |
| 24 | PyYAML | Declared YAML parser dependency | Load and validate one real repository contract, handle an invalid value, and explain safe loading; it currently has no runtime integration |
| 25 | Streamlit | Render the command-center dashboard and optional learning interface | Build or change one source-backed component, handle empty/error state, and explain reruns, cache behavior, and widget state |
| 26 | Plotly | Render interactive KPI charts and tooltips | Build a truthful chart from a governed query, fix a misleading encoding, and defend chart/axis/denominator choices |
| 27 | Streamlit AppTest | Verify dashboard content and interaction without a browser | Author a rendering assertion, diagnose a UI regression, and explain what AppTest does not prove |
| 28 | pytest | Exercise isolated fixtures, model logic, corruptions, and release controls | Write a focused test and fixture, demonstrate red-green behavior, diagnose a false-positive test, and explain test scope |
| 29 | Ruff | Enforce the Python lint contract | Run and interpret lint, fix a real finding, configure one rule deliberately, and explain lint vs tests |
| 30 | Apache Spark | Provide an optional distributed transformation/parity path | Run the Spark job, inspect transformations/output, diagnose a runtime/config issue, and explain when Spark is or is not justified |
| 31 | PySpark | Express the Spark order projection in Python | Implement a bounded DataFrame transformation, test parity against governed IDs, and explain lazy evaluation/shuffles |
| 32 | Java 17 / JVM | Execute the local Spark runtime | Prove the selected JVM, diagnose `JAVA_HOME`/compatibility failure, and explain the Python-to-JVM boundary |
| 33 | Docker Engine / Docker Desktop | Execute the Linux/x86_64 image and isolated runtime gates | Inspect workloads, build/run safely, diagnose a container failure, and explain host mounts, architecture, and resource ownership |
| 34 | Dockerfile | Define the reproducible application image | Change and rebuild a layer, inspect cache behavior, diagnose context/copy issues, and defend ordering/base-image choices |
| 35 | Docker Compose | Define pipeline and dashboard services, ports, mounts, and commands | Run one service safely, explain mount/port behavior, diagnose a service issue, and avoid destructive cleanup |
| 36 | Docker Buildx | Build/load the target Linux architecture | Build for `linux/amd64`, inspect the result, diagnose builder/platform mismatch, and explain `--load` vs registry output |
| 37 | Markdown | Maintain the operational, analytical, and portfolio narrative | Update a technical runbook with linked evidence, review rendered structure, and distinguish claims from receipts |
| 38 | Mermaid | Keep architecture and lineage diagrams reviewable as text | Modify a real diagram, verify semantic accuracy, and explain when a diagram clarifies more than prose |

## Practice order when learning resumes

The default sequence is designed around dependencies, not convenience:

1. Shell, Git, GitHub CLI, GitHub Actions
2. Python, packaging, uv, Make
3. CSV/JSON/YAML/TOML, NumPy, Faker
4. pandas, PyArrow, Parquet, Pandera, PyYAML
5. SQL, DuckDB, dbt, dbt-duckdb, Jinja
6. pytest, Ruff, Streamlit AppTest
7. Streamlit, Plotly
8. Java, Spark, PySpark
9. Dockerfile, Docker Engine/Desktop, Compose, Buildx
10. Markdown and Mermaid as evidence communication

One row may share a realistic scenario with adjacent rows, but each tool receives its own learner-authored action, diagnosis, defense, and retained grade. The agent must not reveal a finished solution before Aneesh's first attempt.
