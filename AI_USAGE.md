# Use of Generative AI

I used Claude (Anthropic) as an assistant throughout this project. This file lists what it did
and what I did, and it will be updated at every stage.

## What the AI did (stage 1)

- Suggested using my Apple Health data as the project topic, among a few options it proposed.
- Wrote the Python scripts in `src/` that turn the Apple Health `export.xml` file into daily and
  hourly tables, including the time-zone conversion and the period labels.
- Proposed counting only iPhone steps to avoid double counting with the Apple Watch.
- Wrote the first version of this README and the "first look" summary table.

## What the AI did (stage 1b: better period labels)

- Looked up Sabancı University's official academic calendars (2023-24 to 2026-27), the MEB
  school calendar, the ÖSYM exam dates and the SU High School Summer School dates.
- Rewrote `src/label_periods.py` so that non-work days are split into high school, exam
  preparation, pre-semester, semester, finals and holiday, and updated the README tables.

## What I did

- Provided the data: my personal Apple Health records since March 2022.
- Chose the topic among the suggested options.
- Provided the dates and context of each life period (market job, restaurant job, travel).
- Questioned the first results: the analysis showed far more night-time steps during the US job,
  and I asked whether this was caused by the time difference. Checking it showed that all
  timestamps had been exported in Istanbul time, which led to the correction described in the
  README.
- Noticed that labelling every non-work day as "school" was wrong (the university is not open
  every day) and asked for the days to be split using the real academic calendar.
- Provided my personal timeline: graduating high school in 2022, a year of studying for the
  university exam at a library, starting Sabancı in September 2023 with the English
  preparatory year, working as a summer-school mentor in 2025, and missing the first week of
  fall 2026 while travelling.
- Reviewed the outputs and uploaded each stage to this repository.
