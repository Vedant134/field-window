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
Winter windows use nine complete seasons within 2015–2024; within-year windows can use ten.
Impossible leap-day endpoints are skipped. Historical windows can differ by one day due to leap years.
Seasonal precipitation totals are rounded to 0.1 mm for display. Calculations start with daily values.

## Method name

Historical seasonal time-series analysis + transparent constraint screening + sensitivity analysis.
No forecasting, machine learning, causal soil-health model, or irrigation model is implemented.

