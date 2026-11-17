"""Aggregate an Apple Health export into a daily table.

Apple Health exports every timestamp in the phone's *current* time zone
(Istanbul, +03:00). Records collected while abroad must be converted back to
the local time zone of the place they were recorded, otherwise hours and day
boundaries are shifted. Periods abroad are listed in LOCATIONS.

Only iPhone sources are used: the Apple Watch was worn only until May 2025,
and counting both would double count steps.
"""
import sys, collections
from datetime import datetime
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
import pandas as pd

path, out = sys.argv[1], sys.argv[2]

TR = ZoneInfo("Europe/Istanbul")
# (start, end) in local dates, inclusive; timezone of that place
LOCATIONS = [
    ("2026-06-12", "2026-10-02", ZoneInfo("America/New_York")),  # Corolla, NC
]
_bounds = [
    (datetime.fromisoformat(s).replace(tzinfo=tz),
     datetime.fromisoformat(e + "T23:59:59").replace(tzinfo=tz), tz)
    for s, e, tz in LOCATIONS
]

def local_time(stamp):
    t = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S %z")
    for lo, hi, tz in _bounds:
        if lo <= t <= hi:
            return t.astimezone(tz)
    return t.astimezone(TR)

SUM = {
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierDistanceWalkingRunning": "distance_km",
    "HKQuantityTypeIdentifierFlightsClimbed": "flights",
}
MEAN = {
    "HKQuantityTypeIdentifierWalkingSpeed": "walking_speed_kmh",
    "HKQuantityTypeIdentifierWalkingStepLength": "step_length_cm",
    "HKQuantityTypeIdentifierHeadphoneAudioExposure": "headphone_db",
}
sums = collections.defaultdict(float)
means = collections.defaultdict(list)
hourly = collections.defaultdict(float)  # (date, hour) -> steps

for ev, el in ET.iterparse(path, events=("end",)):
    if el.tag == "Record":
        t = el.get("type")
        if (t in SUM or t in MEAN) and "Watch" not in (el.get("sourceName") or ""):
            lt = local_time(el.get("startDate"))
            d = lt.date().isoformat()
            v = float(el.get("value"))
            if t in SUM:
                sums[(d, SUM[t])] += v
                if SUM[t] == "steps":
                    hourly[(d, lt.hour)] += v
            else:
                means[(d, MEAN[t])].append(v)
        el.clear()
    elif el.tag in ("Workout", "ActivitySummary"):
        el.clear()

rows = collections.defaultdict(dict)
for (d, k), v in sums.items():
    rows[d][k] = v
for (d, k), vs in means.items():
    rows[d][k] = sum(vs) / len(vs)

active = collections.defaultdict(list)
for (d, h), v in hourly.items():
    if v >= 50:
        active[d].append(h)
for d in rows:
    hs = active.get(d)
    rows[d]["first_active_hour"] = min(hs) if hs else None
    rows[d]["last_active_hour"] = max(hs) if hs else None
    rows[d]["night_steps"] = sum(hourly.get((d, h), 0) for h in range(0, 5))
    rows[d]["evening_steps"] = sum(hourly.get((d, h), 0) for h in range(17, 24))

df = pd.DataFrame.from_dict(rows, orient="index").sort_index()
df.index.name = "date"
df = df.round(2)
df.to_csv(out)

# hourly profile, useful for the "when do I move" figure
hp = pd.Series(hourly).rename_axis(["date", "hour"]).rename("steps").reset_index()
hp.to_csv(out.replace(".csv", "_hourly.csv"), index=False)
print(df.shape)
