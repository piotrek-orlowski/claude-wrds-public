# Optional local Python processing

Use `uv` to manage Python dependencies and run scripts. Do not manually edit dependency manifests or lockfiles. A psql extraction needs no Python environment.

In an existing Python project, add missing packages only when the requested processing needs them:

```bash
uv add pandas pyarrow
uv run python scripts/convert_to_parquet.py
```

A minimal CSV conversion is:

```python
import pandas as pd

df = pd.read_csv("output/results.csv", parse_dates=["date"])
df.to_parquet("output/results.parquet", index=False)
```

Adapt the date column to the actual export; preserve identifiers with leading zeroes as strings. Large CSVs need chunked conversion rather than loading the entire file into RAM. Keep the source CSV until the new file's schema and row counts have been checked.

Prefer `psql` for WRDS extraction. If a task specifically needs an existing Python database pipeline, use `psycopg2.connect("service=wrds")` or a configured SQLAlchemy connection with noninteractive authentication, read-only transactions, and timeouts. Do not use the `wrds` Python package or read authentication files into the script.

PostgreSQL `numeric` may arrive as `decimal.Decimal`; preserve exact values where needed and convert appropriate measurement columns explicitly for NumPy calculations. Handle missing values during conversion. Do not blanket-convert identifier columns or assume every pandas/driver/version combination behaves identically. Cursors are an alternative when a particular `read_sql` integration fails.
