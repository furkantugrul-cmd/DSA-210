# Two Jobs, One Phone: What My iPhone Knows About How Work Changes My Days

DSA 210 (Introduction to Data Science) term project – Sabancı University, Fall 2026

## Motivation

My iPhone has recorded every step I have taken since March 2022. During that time I
alternated between being a university student and doing physical summer jobs:

- **Summer 2022:** supermarket job in Turkey
- **Summer 2026:** line cook at a restaurant in Corolla, North Carolina (USA), on a J-1 work visa

This project uses my own Apple Health data to ask a simple question: **how does a physical
job change the shape of my day compared with student life, and do two very different jobs
change it in the same way?**

## Data

| | |
|---|---|
| Source | My personal Apple Health export (iPhone) |
| Period | 10 March 2022 – 17 November 2026 |
| Size | 1,714 consecutive days, no missing days |
| Daily variables | steps, walking/running distance, flights climbed, walking speed, step length, headphone audio level, first/last active hour, night (00–05) and evening (17–24) steps |
| Hourly variables | steps per hour |

The raw export is **not** published (it contains health records unrelated to this project).
Only the aggregated daily and hourly tables in `data/` are shared.

### Life periods

| Period | Dates | Country | Days |
|---|---|---|---|
| `market_job` | 17 Jul – 2 Sep 2022 | Turkey | 48 |
| `restaurant_job` | 13 Jun – 13 Sep 2026 | USA | 93 |
| `travel` | 12 Jun 2026, 14 Sep – 2 Oct 2026 | USA | 20 |
| `school_normal` | all other days | Turkey | 1,553 |

### Data cleaning decisions

1. **Time-zone correction.** Apple Health exports every timestamp in the phone's *current*
   time zone (Istanbul, UTC+3). Records from my time in the USA were therefore shifted by
   7 hours. Before correction, it looked like I walked about five times more at night during the
   restaurant job; after converting those records back to New York time, the opposite turned out
   to be true. The "night walking" was actually my **evening shift**.
   All USA records are converted to `America/New_York` before computing hours and daily totals.
2. **No double counting.** I also wore an Apple Watch between September 2022 and mid-2025
   (its step records end in May 2025). Steps are counted from the iPhone only, so that the whole
   period is measured with the same device type.
3. **Travel days are separated.** Days spent travelling are labelled `travel` so they do not
   inflate either the work or the normal-life group.

### Known limitations

- **Phone change in May 2025.** Steps were recorded by an iPhone SE (2nd generation) until
  24 May 2025 and by a newer iPhone afterwards. The market job falls in the first phone's period
  and the restaurant job in the second one's, so part of any difference could come from the
  device. This will be checked by comparing normal-life days before and after the change.
- **The phone only counts steps while I carry it.** Steps taken without the phone (for example
  if it was left in a locker during a shift) are not recorded.
- **The last day (17 November 2026) is incomplete**, because the data was exported that day.

## First look

Daily averages per period:

| Period | Steps | Distance (km) | Flights climbed | Evening steps (17–24) | Night steps (00–05) |
|---|---|---|---|---|---|
| Market job (2022) | 21,811 | 16.0 | 12 | 9,899 | 782 |
| Restaurant job (2026) | 12,456 | 9.0 | 29 | 5,447 | 132 |
| School / normal life | 9,351 | 7.0 | 14 | 4,185 | 571 |

These are descriptive numbers only; whether the differences are statistically meaningful is
tested in the hypothesis-testing stage.

## Planned analysis

1. **Exploratory data analysis:** distributions, time series, hourly activity profiles per period,
   weekday vs weekend patterns.
2. **Hypothesis testing**, for example:
   - Do I take more steps on work days than on normal days? (Welch t-test / Mann–Whitney U)
   - Do the market job, the restaurant job and normal life differ from each other? (ANOVA with
     Bonferroni-corrected pairwise comparisons)
   - Is being "highly active" independent of the period? (chi-square test of independence)
3. **Enrichment** with public data (weather, academic calendar) to control for other explanations.
4. **Machine learning:** predict which period a day belongs to from its activity pattern.

## Repository structure

```
├── README.md
├── AI_USAGE.md
├── requirements.txt
├── data/
│   ├── daily_activity.csv   # one row per day, with period labels
│   └── hourly_steps.csv     # steps per hour (local time)
└── src/
    ├── build_daily.py       # Apple Health export.xml -> daily table (time-zone corrected)
    └── label_periods.py     # adds period labels and calendar features
```

## Reproducing

```bash
pip install -r requirements.txt
python src/build_daily.py path/to/export.xml data/daily_raw.csv
python src/label_periods.py data/daily_raw.csv data/daily_activity.csv
```
