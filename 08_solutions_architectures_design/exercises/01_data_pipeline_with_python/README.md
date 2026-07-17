# Data pipeline with Python

ETL exercise from module 08, section 2 (components of an AI solution). A raw retail
orders CSV is extracted with pinned dtypes, transformed (missing-value drop, discount
normalization, IQR outlier removal, KPI and temporal feature engineering), and loaded
back to disk as `clean_orders.csv`.

## Contents

- `data_pipeline_etl.ipynb`: the full ETL flow with per-step rationale.
- `dataset/orders.csv`: the raw input.

## Run

```bash
uv run --with pandas --with numpy --with jupyter jupyter lab
```

Open the notebook and run all cells; the output CSV is regenerated next to it.

The lesson outline targets a further step (extract/transform/load functions, `logging`
instead of `print`, Parquet or PostgreSQL persistence); the closing notes in the
notebook cover what that upgrade would change.
