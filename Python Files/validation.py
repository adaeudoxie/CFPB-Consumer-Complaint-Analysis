"""Validate the cleaned dataset against the raw source.

    python src/validation.py [--input RAW] [--clean CLEAN_CSV]

Writes outputs/validation_results.csv and outputs/validation_results.md and exits non-zero if any check fails.
"""
from __future__ import annotations
import argparse, sys
from datetime import date
import pandas as pd
import config as C
from data_cleaning import load_raw

CHECKS = []


def check(name, category):
    def deco(fn):
        CHECKS.append((name, category, fn)); return fn
    return deco


@check("Raw row count = 62,516", "Completeness")
def _(raw, cl): return len(raw) == C.EXPECTED_ROWS, f"{len(raw):,}"

@check("Raw column count = 12", "Completeness")
def _(raw, cl): return raw.shape[1] == C.EXPECTED_COLS, raw.shape[1]

@check("Cleaned row count equals raw row count (no rows lost)", "Reconciliation")
def _(raw, cl): return len(cl) == len(raw), f"raw {len(raw):,} / clean {len(cl):,}"

@check("Complaint ID unique in raw", "Keys")
def _(raw, cl): return raw["Complaint ID"].is_unique, f"{raw['Complaint ID'].duplicated().sum()} duplicates"

@check("Complaint ID set identical raw vs clean", "Reconciliation")
def _(raw, cl): return set(raw["Complaint ID"]) == set(cl["Complaint ID"]), "set compare"

@check("No fully duplicated rows", "Keys")
def _(raw, cl): return not raw.duplicated().any(), f"{raw.duplicated().sum()}"

@check("Date submitted within 2017-05-01..2023-08-28", "Dates")
def _(raw, cl):
    d = pd.to_datetime(cl["Date submitted"])
    return d.min() == pd.Timestamp(C.EXPECTED_START) and d.max() == pd.Timestamp(C.EXPECTED_END), f"{d.min().date()}..{d.max().date()}"

@check("No date parse failures", "Dates")
def _(raw, cl):
    n = pd.to_datetime(cl["Date submitted"], errors="coerce").isna().sum() + pd.to_datetime(cl["Date received"], errors="coerce").isna().sum()
    return n == 0, n

@check("Forwarding interval never negative", "Dates")
def _(raw, cl): return (cl["Forwarding Interval Days"] >= 0).all(), f"min {cl['Forwarding Interval Days'].min()}"

@check("Forwarding interval recomputes exactly from source dates", "Derived fields")
def _(raw, cl):
    m = raw[["Complaint ID", "Date submitted", "Date received"]].merge(cl[["Complaint ID", "Forwarding Interval Days"]], on="Complaint ID")
    calc = (pd.to_datetime(m["Date received"]) - pd.to_datetime(m["Date submitted"])).dt.days
    bad = (calc != m["Forwarding Interval Days"]).sum(); return bad == 0, f"{bad} mismatches"

@check("Year/Quarter/Month derived correctly", "Derived fields")
def _(raw, cl):
    d = pd.to_datetime(cl["Date submitted"])
    ok = (d.dt.year == cl["Year"]).all() and (d.dt.month == cl["Month Number"]).all() and \
         (("Q" + d.dt.quarter.astype(str)) == cl["Quarter"]).all()
    return ok, "row-level compare"

@check("No missing months between first and last month", "Dates")
def _(raw, cl):
    m = pd.to_datetime(cl["Year Month"]).dt.to_period("M")
    missing = len(set(pd.period_range(m.min(), m.max(), freq="M")) - set(m)); return missing == 0, f"{missing} missing"

@check("Timely blanks are exactly the 'In progress' records", "Business rules")
def _(raw, cl):
    a = raw["Timely response?"].isna(); b = raw["Company response to consumer"] == "In progress"
    return (a == b).all(), f"{a.sum():,} blank / {b.sum():,} in progress"

@check("Timely Response Status: blanks became 'Pending', never 'No'", "Business rules")
def _(raw, cl):
    m = raw[["Complaint ID", "Timely response?"]].merge(cl[["Complaint ID", "Timely Response Status"]], on="Complaint ID")
    ok = (m.loc[m["Timely response?"].isna(), "Timely Response Status"] == "Pending").all() and \
         (m.loc[m["Timely response?"].notna(), "Timely response?"] == m.loc[m["Timely response?"].notna(), "Timely Response Status"]).all()
    return ok, cl["Timely Response Status"].value_counts().to_dict()

@check("Timely KPI denominator = Yes + No only", "Business rules")
def _(raw, cl):
    n = int(cl["Timely Valid For KPI"].sum()); e = int(raw["Timely response?"].isin(["Yes", "No"]).sum())
    return n == e, f"{n:,} valid, {len(cl)-n:,} excluded"

@check("Original categorical values unchanged", "Reconciliation")
def _(raw, cl):
    cols = ["Product", "Issue", "Company response to consumer", "Submitted via", "State"]
    m = raw[["Complaint ID"] + cols].merge(cl[["Complaint ID"] + cols], on="Complaint ID", suffixes=("_r", "_c"))
    bad = sum((m[c + "_r"].astype(str).str.strip() != m[c + "_c"].astype(str)).sum() for c in cols)
    return bad == 0, f"{bad} changed"

@check("Category counts reconcile (Product)", "Reconciliation")
def _(raw, cl):
    return raw["Product"].value_counts().sort_index().equals(cl["Product"].value_counts().sort_index()), "value_counts equal"

@check("Every Product mapped to a short label", "Derived fields")
def _(raw, cl):
    from data_cleaning import PRODUCT_SHORT
    ok = cl["Product"].isin(PRODUCT_SHORT.keys()).all() and cl["Product Short"].nunique() == cl["Product"].nunique()
    return ok, f"{cl['Product Short'].nunique()} short labels for {cl['Product'].nunique()} products"

@check("No blanks left in labelled columns", "Derived fields")
def _(raw, cl):
    cols = ["Sub-product Clean", "Sub-issue Clean", "Public Response Clean", "Timely Response Status", "Forwarding Interval Band"]
    n = int(cl[cols].isna().sum().sum()); return n == 0, f"{n} blanks"

@check("Label counts reconcile to raw blanks", "Reconciliation")
def _(raw, cl):
    ok = ((cl["Sub-issue Clean"] == "No sub-issue recorded").sum() == raw["Sub-issue"].isna().sum() and
          (cl["Public Response Clean"] == "No public response recorded").sum() == raw["Company public response"].isna().sum() and
          (cl["Sub-product Clean"] == "Not provided").sum() == raw["Sub-product"].isna().sum())
    return ok, "sub-issue / public response / sub-product"

@check("Same-attribute groups flagged, not removed", "Business rules")
def _(raw, cl):
    attrs = [c for c in C.RAW_COLUMNS if c != "Complaint ID"]
    exp = int(raw.duplicated(subset=attrs, keep=False).sum())
    got = int(cl["DQ Same-Attribute Group"].astype(bool).sum())
    return got == exp and len(cl) == len(raw), f"{got:,} flagged; {int(cl['DQ Possible Repeat Submission'].astype(bool).sum()):,} possible repeats"


@check("Partial-year flag only on 2017 and 2023", "Derived fields")
def _(raw, cl):
    f = sorted(cl.loc[cl["Is Partial Year"].astype(bool), "Year"].unique().tolist())
    return f == [2017, 2023], f


@check("Partial-month flag only on Aug 2023", "Derived fields")
def _(raw, cl):
    f = cl.loc[cl["Is Partial Month"].astype(bool), "Year Month"].astype(str).str[:7].unique().tolist()
    return f == ["2023-08"], f


def run(raw, cl):
    rows = []
    for name, cat, fn in CHECKS:
        try:
            ok, detail = fn(raw, cl)
        except Exception as e:  # a crashing check is a failed check
            ok, detail = False, f"ERROR: {e}"
        rows.append({"Check": name, "Category": cat, "Result": "PASS" if ok else "FAIL", "Detail": str(detail)})
    return pd.DataFrame(rows)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=str(C.RAW_FILE))
    p.add_argument("--clean", default=str(C.CLEAN_FILE))
    a = p.parse_args(argv)
    raw = load_raw(a.input)
    cl = pd.read_csv(a.clean)
    res = run(raw, cl)
    C.OUTPUTS_DIR.mkdir(exist_ok=True)
    res.to_csv(C.OUTPUTS_DIR / "validation_results.csv", index=False)
    passed = (res["Result"] == "PASS").sum()
    md = [f"# Validation Results", f"_Generated by `src/validation.py` on {date.today()}._", "",
          f"**{passed} of {len(res)} checks passed.**", "",
          "| # | Category | Check | Result | Detail |", "|---|---|---|---|---|"]
    md += [f"| {i} | {r.Category} | {r.Check} | {'✅' if r.Result=='PASS' else '❌'} {r.Result} | {r.Detail.replace('|','/')} |"
           for i, r in enumerate(res.itertuples(), 1)]
    (C.OUTPUTS_DIR / "validation_results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(res.to_string(index=False))
    print(f"\n{passed}/{len(res)} passed")
    sys.exit(0 if passed == len(res) else 1)


if __name__ == "__main__":
    main()
