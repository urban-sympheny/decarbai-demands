# Claude Code project context — decarbAI-demands

## What this project is

A Dash dashboard that runs a per-city, per-building-type XGBoost + PCA ensemble to predict 8760-hour heating, cooling, electricity, and DHW demand profiles for Swiss buildings. Inputs are validated with Pydantic, geometry-derived features are computed, and 17 features in a fixed order are fed to the model artifacts under `~/.cache/decarbai/models/` (downloaded on first use from S3).

## Run

```powershell
uv run python -m decarbai_demands.dashboard          # launches the UI at http://127.0.0.1:8050/
uv run python -m decarbai_demands.pipeline           # smoke-runs the pipeline, writes test.csv
```

## Stack

Python 3.11+, Dash 4, Pydantic 2, XGBoost, NumPy, zstandard. Environments managed via `uv`.

## Mandatory post-task checks (the only checks Claude runs)

After **every** task — refactor, feature, fix — run all three and make sure they exit 0:

```powershell
uv run ruff check src
uv run ruff format --check src
uv run mypy src
```

If any fail, fix the root cause before declaring the task done. Don't paper over with `# type: ignore` or `# noqa` without a comment explaining the constraint.

The user verifies feature behaviour themselves. Don't add or run additional smoke tests / integration tests / dashboard launches unless explicitly asked.

## Keep docs in sync

After every task, check whether the change affects anything documented in [README.md](README.md) (directory tree, module purposes, training ranges, run commands) or in this file (invariants, layout, style rules, run commands). If yes, update the relevant doc in the same task. If the change is purely internal and nothing documented shifted, leave both files alone — don't churn docs for no reason.

## Repo layout

See [README.md](README.md) for the directory tree and module purposes. The dashboard is a subpackage under `src/decarbai_demands/dashboard/`; inference lives in `schema.py` + `model.py` + `pipeline.py` at the package root.

## Load-bearing invariants (do not silently change)

- **The 17-feature vector order** in [src/decarbai_demands/schema.py](src/decarbai_demands/schema.py) (`InputData.ordered_features`) is glued to the model weights. Reordering it breaks predictions silently — no exception, just wrong numbers.
- **Model directory layout** `~/.cache/decarbai/models/<country>/<city>/<building_type>/<demand>.zst`. `ensure_city_models(country, city)` in `model_cache.py` downloads and extracts the city archive on first use. `pipeline.run_pipeline` calls this before building `model_base_path`.
- **`electricity_dhw.zst` returns one concatenated profile**: indices `0..8760` are DHW, `8760..` are electricity. Don't reorder the split in [pipeline.py](src/decarbai_demands/pipeline.py).
- **Training ranges** are inlined in [src/decarbai_demands/dashboard/ranges.py](src/decarbai_demands/dashboard/ranges.py) and mirrored in the README. The dashboard reads them at import — no JSON file on disk.

## Style preferences

- Ruff: line-length 150, mccabe max-complexity 10, full ruleset in [pyproject.toml](pyproject.toml). Don't reformat unrelated files.
- Mypy: `disallow_untyped_defs`, `warn_return_any` — every new function needs full annotations.
- Prefer editing existing files to creating new ones.
- Default to no comments. Only add one when the *why* is non-obvious.
- Don't add backwards-compat shims or hypothetical-future scaffolding.
- The dashboard subpackage is split by concern: `styles.py`, `constants.py`, `ranges.py`, `layout.py`, `callbacks.py`, `app.py`. Add new UI sections to `layout.py`, new callbacks to `callbacks.py` — don't grow `app.py`.
