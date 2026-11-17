"""Add life-period labels and calendar features to the daily table.

Usage: python src/label_periods.py data/daily_raw.csv data/daily_activity.csv

Every day gets exactly one `period` label. Labels are assigned in two passes:

1. Base calendar: high school, the exam-preparation year, and Sabancı University
   semesters taken from the official academic calendars
   (https://www.sabanciuniv.edu/en/academic-calendar). Days that fall outside any
   school period are `holiday`.
2. Overrides: jobs and travel replace whatever the calendar says for those days.

Weekends are NOT treated as holidays; use the `is_weekend` column for that.
"""
import sys
import pandas as pd

PRE_SEMESTER_DAYS = 7  # days before the first class labelled `pre_semester`

# ---------------------------------------------------------------------------
# 1. Base calendar
# ---------------------------------------------------------------------------
# High school (12th grade). MEB 2021-22 school year ended 17 Jun 2022 and
# YKS 2022 was on 18-19 Jun 2022, so the school period runs until the exam.
HIGH_SCHOOL = [("2022-03-10", "2022-06-19")]
HIGH_SCHOOL_BREAKS = [("2022-04-11", "2022-04-15")]  # MEB spring mid-term break

# Exam-preparation year after graduating: studied for YKS 2023 at a library.
# Ends with YKS 2023 (17-18 Jun 2023).
EXAM_PREP = [("2022-09-03", "2023-06-18")]

# Sabancı University semesters (undergraduate calendar).
# first_class, last_class, last_exam_day (finals incl. make-up exams).
# 2023-24 was the English preparatory year (FDY); its fall and spring terms
# started on the same day as the faculty calendar (FDY classes began 2 Oct 2023),
# so the university calendar is used for it as well.
SEMESTERS = [
    # name,          first_class,  last_class,   last_exam
    ("fall_2023",   "2023-10-02", "2024-01-05", "2024-01-19"),
    ("spring_2024", "2024-02-15", "2024-05-29", "2024-06-09"),
    ("fall_2024",   "2024-09-23", "2024-12-31", "2025-01-12"),
    ("spring_2025", "2025-02-05", "2025-05-23", "2025-06-04"),
    ("fall_2025",   "2025-09-29", "2026-01-03", "2026-01-16"),
    ("spring_2026", "2026-02-16", "2026-05-22", "2026-06-13"),
    ("fall_2026",   "2026-09-28", "2026-12-31", "2027-01-16"),
]

# Week-long breaks inside a semester (single public holidays are ignored,
# like weekends).
SEMESTER_BREAKS = [
    ("2024-04-08", "2024-04-12"),  # spring break / Ramadan holiday
    ("2025-03-31", "2025-04-04"),  # spring break
    ("2026-03-19", "2026-03-22"),  # spring break / Ramadan holiday
]

# ---------------------------------------------------------------------------
# 2. Overrides: jobs and travel (applied last, so they always win)
# ---------------------------------------------------------------------------
OVERRIDES = [
    ("2022-07-17", "2022-09-02", "market_job", "Turkey"),        # supermarket job
    ("2025-07-07", "2025-08-15", "summer_school_mentor", "Turkey"),  # SU High School Summer School, 3 sessions
    ("2026-06-12", "2026-06-12", "travel", "USA"),               # arrival day
    ("2026-06-13", "2026-09-13", "restaurant_job", "USA"),       # line cook, Corolla NC
    ("2026-09-14", "2026-10-02", "travel", "USA"),               # travel after the job (missed 1st week of fall 2026)
]

GROUP = {
    "high_school": "school",
    "exam_prep": "school",
    "semester": "school",
    "finals": "school",
    "pre_semester": "break",
    "holiday": "break",
    "market_job": "work",
    "restaurant_job": "work",
    "summer_school_mentor": "work",
    "travel": "travel",
}


def label(df: pd.DataFrame) -> pd.DataFrame:
    d = df["date"]
    df["period"] = "holiday"
    df["semester"] = pd.NA
    df["country"] = "Turkey"

    def set_range(start, end, value, col="period"):
        df.loc[d.between(start, end), col] = value

    for s, e in HIGH_SCHOOL:
        set_range(s, e, "high_school")
    for s, e in HIGH_SCHOOL_BREAKS:
        set_range(s, e, "holiday")
    for s, e in EXAM_PREP:
        set_range(s, e, "exam_prep")

    for name, first, last_class, last_exam in SEMESTERS:
        first_ts = pd.Timestamp(first)
        pre_start = first_ts - pd.Timedelta(days=PRE_SEMESTER_DAYS)
        pre_end = first_ts - pd.Timedelta(days=1)
        finals_start = pd.Timestamp(last_class) + pd.Timedelta(days=1)
        set_range(pre_start, pre_end, "pre_semester")
        set_range(first, last_class, "semester")
        set_range(finals_start, last_exam, "finals")
        set_range(first, last_exam, name, col="semester")
    for s, e in SEMESTER_BREAKS:
        set_range(s, e, "holiday")

    for s, e, lab, country in OVERRIDES:
        set_range(s, e, lab)
        set_range(s, e, country, col="country")

    df["period_group"] = df["period"].map(GROUP)
    df["is_work"] = df["period_group"].eq("work")
    df["weekday"] = d.dt.day_name()
    df["is_weekend"] = d.dt.dayofweek >= 5
    df["year"] = d.dt.year
    df["month"] = d.dt.month
    return df


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    df = pd.read_csv(src, parse_dates=["date"])
    # allow re-labelling an already labelled table
    df = df.drop(columns=[c for c in ["period", "semester", "country", "period_group", "is_work",
                                      "weekday", "is_weekend", "year", "month"] if c in df.columns])
    df = label(df)
    assert df["period_group"].notna().all()
    df.to_csv(out, index=False)
    print(df.groupby("period")[["steps", "distance_km", "flights", "evening_steps", "night_steps"]]
          .agg(["count", "mean"]).round(0).T)
