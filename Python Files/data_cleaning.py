"""Reproducible cleaning pipeline: raw Excel -> cleaned CSV.

Usage:
    python src/data_cleaning.py [--input PATH] [--output PATH]

Principles
- The raw file is read-only; nothing is written back to it.
- No rows are removed (0 duplicate IDs, 0 duplicate rows in the source).
- Original columns keep their original values; every cleaned/derived value goes in a NEW column,
  so each transformation can be traced back to the source value.
"""
from __future__ import annotations
import argparse
import numpy as np
import pandas as pd
import config as C

PRODUCT_SHORT = {
    "Checking or savings account": "Checking/Savings",
    "Credit card or prepaid card": "Credit/Prepaid Card",
    "Credit reporting, credit repair services, or other personal consumer reports": "Credit Reporting",
    "Mortgage": "Mortgage",
    "Money transfer, virtual currency, or money service": "Money Transfer",
    "Debt collection": "Debt Collection",
    "Vehicle loan or lease": "Vehicle Loan/Lease",
    "Payday loan, title loan, or personal loan": "Payday/Personal Loan",
    "Student loan": "Student Loan",
}
PUBLIC_RESPONSE_SHORT = {
    "Company has responded to the consumer and the CFPB and chooses not to provide a public response": "Chose not to respond publicly",
    "Company believes the complaint provided an opportunity to answer consumer's questions": "Opportunity to answer questions",
    "Company believes the complaint is the result of a misunderstanding": "Result of a misunderstanding",
    "Company believes it acted appropriately as authorized by contract or law": "Acted appropriately (contract/law)",
    "Company believes complaint caused principally by actions of third party outside the control or direction of the company": "Caused by third party",
    "Company disputes the facts presented in the complaint": "Disputes the facts",
}
INTERVAL_BANDS = [(-1, 0, "0 days (same day)"), (0, 1, "1 day"), (1, 7, "2-7 days"),
                  (7, 30, "8-30 days"), (30, np.inf, "Over 30 days")]


def load_raw(path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=C.SHEET)
    missing = set(C.RAW_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Raw file is missing expected columns: {missing}")
    return df[C.RAW_COLUMNS].copy()


def clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # 1. Types and text hygiene
    out["Date submitted"] = pd.to_datetime(out["Date submitted"]).dt.normalize()
    out["Date received"] = pd.to_datetime(out["Date received"]).dt.normalize()
    for col in ["Submitted via", "State", "Product", "Sub-product", "Issue", "Sub-issue",
                "Company public response", "Company response to consumer", "Timely response?"]:
        out[col] = out[col].astype("string").str.strip()

    # 2. Calendar fields (based on Date submitted = date the CFPB received the complaint)
    ds = out["Date submitted"]
    out["Year"] = ds.dt.year
    out["Quarter"] = "Q" + ds.dt.quarter.astype(str)
    out["Year Quarter"] = out["Year"].astype(str) + " " + out["Quarter"]
    out["Month Number"] = ds.dt.month
    out["Month Name"] = ds.dt.strftime("%b")
    out["Year Month"] = ds.dt.to_period("M").dt.to_timestamp()  # first day of month
    first_day, last_day = pd.Timestamp(C.EXPECTED_START), pd.Timestamp(C.EXPECTED_END)
    out["Is Partial Month"] = (ds.dt.to_period("M") == last_day.to_period("M"))
    # 2017 covers May-Dec only; 2023 covers Jan-28 Aug only.
    out["Is Partial Year"] = out["Year"].isin([first_day.year, last_day.year])

    # 3. CFPB forwarding interval (NOT company response/resolution time)
    out["Forwarding Interval Days"] = (out["Date received"] - out["Date submitted"]).dt.days
    out["Forwarding Interval Band"] = pd.cut(
        out["Forwarding Interval Days"],
        bins=[b[0] for b in INTERVAL_BANDS] + [np.inf],
        labels=[b[2] for b in INTERVAL_BANDS]).astype("string")
    out["Is Long Forwarding Interval"] = out["Forwarding Interval Days"] > C.LONG_INTERVAL_DAYS

    # 4. Categorical labels (originals untouched)
    out["Product Short"] = out["Product"].map(PRODUCT_SHORT).fillna(out["Product"])
    out["Sub-product Clean"] = out["Sub-product"].fillna("Not provided")
    out["Sub-issue Clean"] = out["Sub-issue"].fillna("No sub-issue recorded")
    out["Public Response Clean"] = (out["Company public response"].map(PUBLIC_RESPONSE_SHORT)
                                    .fillna(out["Company public response"])
                                    .fillna("No public response recorded"))

    # 5. Timely response: blank != No. Blanks coincide with 'In progress' -> 'Pending'.
    out["Timely Response Status"] = out["Timely response?"].fillna("Pending")
    out["Timely Valid For KPI"] = out["Timely response?"].isin(["Yes", "No"])
    out["Is In Progress"] = out["Company response to consumer"] == "In progress"

    # 6. Data-quality flags (documented, not "fixed")
    out["DQ Missing Sub-product"] = out["Sub-product"].isna()
    out["DQ Missing Public Response"] = out["Company public response"].isna()
    # Distinct Complaint IDs whose 11 other attributes are identical to another record.
    # Kept (distinct IDs = distinct complaints per the brief); flagged so analysts can test sensitivity.
    attrs = [c for c in C.RAW_COLUMNS if c != "Complaint ID"]
    out["DQ Same-Attribute Group"] = df.duplicated(subset=attrs, keep=False).values
    grp_span = df.groupby(attrs, dropna=False)["Complaint ID"].transform(lambda s: s.max() - s.min())
    out["DQ Possible Repeat Submission"] = (out["DQ Same-Attribute Group"] & (grp_span.values <= 5))

    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default=str(C.RAW_FILE))
    p.add_argument("--output", default=str(C.CLEAN_FILE))
    a = p.parse_args(argv)
    raw = load_raw(a.input)
    cleaned = clean(raw)
    from pathlib import Path
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(a.output, index=False, date_format="%Y-%m-%d")
    print(f"Read {len(raw):,} rows from {a.input}")
    print(f"Wrote {len(cleaned):,} rows x {cleaned.shape[1]} columns to {a.output}")


if __name__ == "__main__":
    main()
