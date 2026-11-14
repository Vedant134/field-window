# The math, in plain words

We summarize past weather. We do not predict the future or calculate a best crop score.

## 1. How much time does the farmer have?

Available days = next planting date − date the field becomes available.

Example: October 15 to March 1 gives 137 days in the demonstration year.
If the scenario reserves 20 days for transition, potential growing time = 137 − 20 = 117 days.
That does NOT prove a crop can mature in 117 days. We do not yet have a validated crop growth model.
The end date belongs to the next crop and is excluded from weather totals.

## 2. How much precipitation fell?

For each historical season, add daily precipitation during that same calendar window:

R = r1 + r2 + ... + rn

If three days have 2, 0, and 5 mm, the total is 7 mm.
NASA's daily precipitation is in mm/day; summing over daily steps gives mm.
This is precipitation input, not crop water use, stored soil water, or irrigation needed.

## 3. What is a typical historical total?

Sort the seasonal totals. The median is the middle value; for an even number, average the middle two.
Example: 100, 180, 220, 300, 500 mm → median 220 mm; observed range 100–500 mm.
These numbers illustrate arithmetic only, not downloaded Merced results.
The range shows the observed spread, not a confidence interval or future forecast.

## 4. How often did a temperature event occur?

For each day, count 1 if the temperature meets the condition and 0 otherwise. Add the counts.
We report daily minimum temperature at or below 0°C as general freezing context.
The oat example also counts historical windows containing at least one day at or below −8°C.
That literature-based screen identifies regional cold exposure; it is not a validated injury or survival model.
Example: two exposed seasons out of nine → 2/9 historical windows. Do not call this a future failure probability.

## 5. When did the precipitation arrive?

Cumulative precipitation on day k = the sum of precipitation from day 1 through day k.
For 2, 0, and 5 mm, the curve shows 2, 2, and 7 mm.
We select the lowest-total, middle-ranked, and highest-total seasons and plot their cumulative curves.
This shows timing differences. It does not establish whether plants received enough water.

## 6. How do the comparisons work?

Documented checks and explicit unknowns, not learned coefficients:
- Start month: compare with the broad winter-oat planting months in the reference catalog.
- Calendar allocation: subtract the scenario transition interval.
- Cold exposure: report the historical count against the reference threshold.
- Goal alignment: cover versus feed use. This is a stated preference, not a numerical agronomy score.
- Unknown: growth duration, harvest readiness, soil/pest compatibility, water sufficiency, yield, and profit.

Changing reserved transition time from 20 to 30 days reduces potential growing time by 10 days.
That is sensitivity analysis: vary one assumption and see its effect.

## 7. Data quality and historical windows

We require valid observations for all four requested variables for each day of a season.
Missing observations exclude that whole historical season from the comparison.
The archive is 1995–2024. Windows that cross New Year can use 29 seasons; within-year windows can use 30.
A 29 February start or end date is treated as 28 February in non-leap years. Historical windows can differ by one day due to leap years.
Seasonal precipitation totals are rounded to 0.1 mm for display. Calculations start with daily values.

## 8. Rain against atmospheric demand

Growing days = the window minus the reserved transition days, counted from the start.
For each growing day we estimate reference evapotranspiration with the Hargreaves equation (FAO-56, equation 52):

ET0 = 0.0023 × (Tmean + 17.8) × √(Tmax − Tmin) × 0.408 × Ra, in mm/day

Tmean is (Tmax + Tmin) / 2. Ra is the sunlight reaching the top of the atmosphere for that latitude and day of year (FAO-56, equation 21), in MJ per square metre per day.
Example: Tmin 15, Tmax 25, Ra 30 → 0.0023 × 37.8 × 3.162 × 0.408 × 30 = 3.4 mm/day.
We sum ET0 and rain over the growing days of each season and count the seasons where rain was at least as large.
ET0 describes a well-watered reference grass surface. It is not the water use of oats or any crop, and soil storage is ignored.
Hargreaves uses temperature only; it can read high in humid places and low in windy ones.

## 9. Wet days at the start and the finish

A wet day has at least 1 mm of precipitation.
We count wet days in the first 14 and the last 14 growing days of each season, and the number of days until the first wet day.
Reported as medians, the middle half of seasons (25th to 75th percentile), and “k of n seasons had none.”
Moving the transition slider moves the last 14 growing days, so these counts change. That is the sensitivity analysis.
These are historical frequencies. With about 30 seasons, a count such as 21 of 29 is a description of the record, not a precise probability.

## 10. Root-zone wetness

NASA POWER supplies a modelled root-zone soil wetness between 0 and 1 (MERRA-2). We report its value on the first day of each season.
It is a regional model output, not a field measurement, and a missing value never excludes a season.

## Method name

Historical seasonal time-series analysis + transparent constraint screening + sensitivity analysis.
No forecasting, machine learning, causal soil-health model, or irrigation model is implemented.

