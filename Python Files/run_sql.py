"""Load the cleaned CSV into SQLite and run every named query in a .sql file.

    python src/run_sql.py [--clean PATH] [--sql sql/kpi_calculations.sql] [--prefix SQL_]

Each "-- name: X" block is executed and saved to outputs/kpi_outputs/<prefix>X.csv.
"""
from __future__ import annotations
import argparse, re, sqlite3
import pandas as pd
import config as C

BOOL_COLS = ["Is Partial Month", "Is Partial Year", "Is Long Forwarding Interval", "Timely Valid For KPI",
             "Is In Progress", "DQ Missing Sub-product", "DQ Missing Public Response",
             "DQ Same-Attribute Group", "DQ Possible Repeat Submission"]


def connect(clean_path) -> sqlite3.Connection:
    df = pd.read_csv(clean_path)
    for c in BOOL_COLS:
        df[c] = df[c].astype(bool).astype(int)
    con = sqlite3.connect(":memory:")
    df.to_sql("complaints", con, index=False)
    return con


def named_queries(sql_text: str) -> dict[str, str]:
    parts = re.split(r"^--\s*name:\s*(\S+)\s*$", sql_text, flags=re.M)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", default=str(C.CLEAN_FILE))
    ap.add_argument("--sql", default=str(C.REPO_ROOT / "sql" / "kpi_calculations.sql"))
    ap.add_argument("--prefix", default="SQL_")
    a = ap.parse_args(argv)
    con = connect(a.clean)
    out = C.OUTPUTS_DIR / "kpi_outputs"; out.mkdir(parents=True, exist_ok=True)
    qs = named_queries(open(a.sql, encoding="utf-8").read())
    for name, q in qs.items():
        pd.read_sql_query(q, con).to_csv(out / f"{a.prefix}{name}.csv", index=False)
    print(f"Ran {len(qs)} queries from {a.sql}")


if __name__ == "__main__":
    main()
