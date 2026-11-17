"""Calculate the 12 required KPIs (brief §5-B) from the cleaned dataset.

    python src/analysis.py [--clean PATH]

Writes one CSV per KPI table to outputs/kpi_outputs/ (prefix PY_) and outputs/kpi_summary.md.
The same KPIs are calculated independently in SQL (sql/kpi_calculations.sql, run by src/run_sql.py)
and compared in src/cross_check.py.
"""
from __future__ import annotations
import argparse
from datetime import date
import pandas as pd
import config as C

OUT = C.OUTPUTS_DIR / "kpi_outputs"


def load(path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["Date submitted", "Date received", "Year Month"])


def share(counts: pd.Series, total: int) -> pd.Series:
    return (counts / total * 100).round(2)


def kpis(d: pd.DataFrame) -> dict[str, pd.DataFrame]:
    n = len(d)
    k = {}
    # K01 Total complaints
    k["K01_total_complaints"] = pd.DataFrame({"total_complaints": [n]})

    # K02 Annual complaint volume
    y = d.groupby("Year").agg(complaints=("Complaint ID", "size"),
                              is_partial_year=("Is Partial Year", "max")).reset_index()
    y["is_partial_year"] = y["is_partial_year"].astype(int)
    k["K02_annual_volume"] = y.rename(columns={"Year": "year"})

    # K03 Monthly complaint volume
    m = d.groupby(d["Year Month"].dt.strftime("%Y-%m")).agg(
        complaints=("Complaint ID", "size"), is_partial_month=("Is Partial Month", "max")).reset_index()
    m["is_partial_month"] = m["is_partial_month"].astype(int)
    k["K03_monthly_volume"] = m.rename(columns={"Year Month": "year_month"})

    # K04 + K07 Complaints by product and % contribution
    p = d["Product"].value_counts().rename_axis("product").reset_index(name="complaints")
    p["pct_of_total"] = share(p["complaints"], n)
    k["K04_K07_by_product"] = p

    # K05 Complaints by issue
    i = d["Issue"].value_counts().rename_axis("issue").reset_index(name="complaints")
    i["pct_of_total"] = share(i["complaints"], n)
    k["K05_by_issue"] = i

    # K06 Complaints by sub-product and by sub-issue (labelled blanks kept visible)
    sp = d.groupby(["Product", "Sub-product Clean"]).size().reset_index(name="complaints") \
          .rename(columns={"Product": "product", "Sub-product Clean": "sub_product"}) \
          .sort_values(["complaints", "product", "sub_product"], ascending=[False, True, True], ignore_index=True)
    k["K06a_by_sub_product"] = sp
    si = d.groupby(["Issue", "Sub-issue Clean"]).size().reset_index(name="complaints") \
          .rename(columns={"Issue": "issue", "Sub-issue Clean": "sub_issue"}) \
          .sort_values(["complaints", "issue", "sub_issue"], ascending=[False, True, True], ignore_index=True)
    k["K06b_by_sub_issue"] = si

    # K08 Company response category distribution
    r = d["Company response to consumer"].value_counts().rename_axis("company_response").reset_index(name="complaints")
    r["pct_of_total"] = share(r["complaints"], n)
    k["K08_response_distribution"] = r
    pr = d["Public Response Clean"].value_counts().rename_axis("public_response").reset_index(name="complaints")
    pr["pct_of_total"] = share(pr["complaints"], n)
    k["K08b_public_response_distribution"] = pr

    # K09 Timely response % (denominator = Yes + No only; Pending reported separately)
    yes = int((d["Timely Response Status"] == "Yes").sum())
    no = int((d["Timely Response Status"] == "No").sum())
    pend = int((d["Timely Response Status"] == "Pending").sum())
    k["K09_timely_response"] = pd.DataFrame({
        "timely_yes": [yes], "timely_no": [no], "valid_denominator": [yes + no],
        "excluded_pending": [pend], "timely_pct": [round(yes / (yes + no) * 100, 2)]})
    ty = d[d["Timely Valid For KPI"]].groupby("Year")["Timely Response Status"] \
        .agg(timely_yes=lambda s: int((s == "Yes").sum()), timely_no=lambda s: int((s == "No").sum())).reset_index()
    ty["timely_pct"] = (ty["timely_yes"] / (ty["timely_yes"] + ty["timely_no"]) * 100).round(2)
    k["K09b_timely_by_year"] = ty.rename(columns={"Year": "year"})

    # K10 Complaints In progress
    k["K10_in_progress"] = pd.DataFrame({"in_progress": [int(d["Is In Progress"].sum())]})

    # K11 Average and median CFPB forwarding interval
    fi = d["Forwarding Interval Days"]
    k["K11_forwarding_interval"] = pd.DataFrame({
        "avg_days": [round(fi.mean(), 2)], "median_days": [float(fi.median())],
        "max_days": [int(fi.max())], "over_30_days": [int((fi > C.LONG_INTERVAL_DAYS).sum())]})
    fp = d.groupby("Product")["Forwarding Interval Days"].agg(
        complaints="size", avg_days="mean", median_days="median",
        over_30_days=lambda s: int((s > C.LONG_INTERVAL_DAYS).sum())).reset_index()
    fp["avg_days"] = fp["avg_days"].round(2)
    fp["median_days"] = fp["median_days"].astype(float)
    k["K11b_forwarding_by_product"] = fp.rename(columns={"Product": "product"}).sort_values("avg_days", ascending=False, ignore_index=True)

    # K12 Year-over-year change: calendar years (partial years flagged) and like-for-like (1 Jan - 28 Aug)
    y = k["K02_annual_volume"].copy()
    y["prev_year_complaints"] = y["complaints"].shift(1)
    y["yoy_change"] = y["complaints"] - y["prev_year_complaints"]
    y["yoy_pct"] = (y["yoy_change"] / y["prev_year_complaints"] * 100).round(2)
    y["comparison_valid"] = ((y["is_partial_year"] == 0) & (y["is_partial_year"].shift(1) == 0)).astype(int)
    k["K12_yoy_calendar"] = y
    ds = d["Date submitted"]
    ytd = d[(ds.dt.month < 8) | ((ds.dt.month == 8) & (ds.dt.day <= 28))]
    l = ytd.groupby("Year").size().reset_index(name="complaints_jan1_to_aug28").rename(columns={"Year": "year"})
    l = l[l["year"] >= 2018].reset_index(drop=True)  # 2017 has no Jan-Apr data
    l["prev"] = l["complaints_jan1_to_aug28"].shift(1)
    l["yoy_pct"] = ((l["complaints_jan1_to_aug28"] - l["prev"]) / l["prev"] * 100).round(2)
    k["K12b_yoy_like_for_like"] = l.drop(columns="prev")
    return k


def summary_md(k) -> str:
    t, ti, fi = k["K01_total_complaints"].iloc[0], k["K09_timely_response"].iloc[0], k["K11_forwarding_interval"].iloc[0]
    p = k["K04_K07_by_product"].iloc[0]; i = k["K05_by_issue"].iloc[0]; r = k["K08_response_distribution"].iloc[0]
    y = k["K12_yoy_calendar"]; full = y[y["is_partial_year"] == 0]
    lines = [
        "# KPI Summary", f"_Generated by `src/analysis.py` on {date.today()}. Detail tables are in `outputs/kpi_outputs/`._", "",
        "| # | KPI | Value |", "|---|---|---|",
        f"| 1 | Total complaints | {t.total_complaints:,} |",
        f"| 2 | Annual volume | Peak full year {int(full.loc[full.complaints.idxmax(),'year'])}: {full.complaints.max():,}. 2017 and 2023 are partial years |",
        f"| 3 | Monthly volume | {len(k['K03_monthly_volume'])} months. Highest: {k['K03_monthly_volume'].sort_values('complaints').iloc[-1].year_month} ({k['K03_monthly_volume'].complaints.max():,}) |",
        f"| 4 | Top product | {p['product']}: {p.complaints:,} |",
        f"| 5 | Top issue | {i.issue}: {i.complaints:,} ({i.pct_of_total}%) |",
        f"| 6 | Sub-product / sub-issue combinations | {len(k['K06a_by_sub_product'])} product–sub-product pairs. {len(k['K06b_by_sub_issue'])} issue–sub-issue pairs |",
        f"| 7 | Top product share | {p.pct_of_total}% of all complaints |",
        f"| 8 | Most common company response | {r.company_response}: {r.complaints:,} ({r.pct_of_total}%) |",
        f"| 9 | Timely response % | **{ti.timely_pct}%** ({int(ti.timely_yes):,} Yes ÷ {int(ti.valid_denominator):,} Yes+No). {int(ti.excluded_pending):,} pending excluded |",
        f"| 10 | In progress | {k['K10_in_progress'].iloc[0].in_progress:,} |",
        f"| 11 | CFPB forwarding interval | Average {fi.avg_days} days, median {fi.median_days:g} days. {int(fi.over_30_days):,} over 30 days (max {int(fi.max_days)}) |",
        f"| 12 | YoY change (full years) | " + ", ".join(f"{int(r.year)}: {r.yoy_pct:+.2f}%" for r in y[y.comparison_valid == 1].itertuples()) + " |",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--clean", default=str(C.CLEAN_FILE)); a = ap.parse_args(argv)
    k = kpis(load(a.clean))
    OUT.mkdir(parents=True, exist_ok=True)
    for name, df in k.items():
        df.to_csv(OUT / f"PY_{name}.csv", index=False)
    (C.OUTPUTS_DIR / "kpi_summary.md").write_text(summary_md(k), encoding="utf-8")
    print(f"Wrote {len(k)} KPI tables to {OUT}")


if __name__ == "__main__":
    main()
