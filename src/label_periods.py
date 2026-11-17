"""Add life-period labels and calendar features to the daily table.

Usage: python src/label_periods.py data/daily_raw.csv data/daily_activity.csv
"""
import sys
import pandas as pd

src, out = sys.argv[1], sys.argv[2]

# Life periods (inclusive dates). Everything else is "school/normal".
PERIODS = [
    ("2022-07-17", "2022-09-02", "market_job", "Turkey"),        # supermarket job
    ("2026-06-12", "2026-06-12", "travel", "USA"),               # arrival day
    ("2026-06-13", "2026-09-13", "restaurant_job", "USA"),       # line cook, Corolla NC
    ("2026-09-14", "2026-10-02", "travel", "USA"),               # travel after the job
]

df = pd.read_csv(src, parse_dates=["date"])
df["period"] = "school_normal"
df["country"] = "Turkey"
for start, end, label, country in PERIODS:
    mask = df["date"].between(start, end)
    df.loc[mask, "period"] = label
    df.loc[mask, "country"] = country

df["is_work"] = df["period"].isin(["market_job", "restaurant_job"])
df["weekday"] = df["date"].dt.day_name()
df["is_weekend"] = df["date"].dt.dayofweek >= 5
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

df.to_csv(out, index=False)
print(df.groupby("period")[["steps", "distance_km", "flights", "evening_steps", "night_steps"]]
      .agg(["count", "mean"]).round(0).T)
