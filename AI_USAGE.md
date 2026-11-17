# Use of Generative AI

I used Claude (Anthropic) as an assistant throughout this project. This file lists what it did
and what I did, and it will be updated at every stage.

## What the AI did (stage 1)

- Suggested using my Apple Health data as the project topic, among a few options it proposed.
- Wrote the Python scripts in `src/` that turn the Apple Health `export.xml` file into daily and
  hourly tables, including the time-zone conversion and the period labels.
- Proposed counting only iPhone steps to avoid double counting with the Apple Watch.
- Wrote the first version of this README and the "first look" summary table.

## What I did

- Provided the data: my personal Apple Health records since March 2022.
- Chose the topic among the suggested options.
- Provided the dates and context of each life period (market job, restaurant job, travel).
- Questioned the first results: the analysis showed far more night-time steps during the US job,
  and I asked whether this was caused by the time difference. Checking it showed that all
  timestamps had been exported in Istanbul time, which led to the correction described in the
  README.
- Reviewed the outputs and uploaded each stage to this repository.
