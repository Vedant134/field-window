# Judge walkthrough

## Problem
Farmers considering a crop between two existing crops must balance timing, water uncertainty, management effort, and the intended use. A weather chart alone does not make that comparison.

## What we built
A decision-support prototype with worldwide city/coordinate weather lookup. Merced is the initial regional crop-guidance example. Outside that area, the app shows generic scenarios and explicitly requests regional crop evidence. It compares current gap management with oats for cover and oats for forage. The alternatives are management scenarios of one species; the complete local crop sequence still needs validation.

## Why NASA matters
Daily NASA POWER observations provide the historical environmental context. The app summarizes the same calendar window across past years, shows precipitation variability and timing, and reports temperature exposure. Agricultural references contribute crop context. Farmer inputs supply dates, current practice, and irrigation category.

## The analysis
Data cleaning → complete-season selection → seasonal time-series summaries → sourced constraint checks → sensitivity analysis → explanations.

## Visual demonstration
Show annual precipitation totals, then cumulative rainfall in dry/middle/wet seasons. Show the rotation-window timeline. Increase reserved transition time and watch available growing time shrink. Switch the farmer's goal to reveal the difference between potential soil-cover value and feed use.

## Why one option over another?
We explain goal alignment and constraints separately. Oats for cover directly serves a cover/residue objective; forage serves a feed objective but requires harvest readiness and equipment. Neither is automatically superior. Water, crop compatibility, and biological growth remain uncertain.

## Limitations
Historical observations are not forecasts. No yield/profit/water-saving prediction. No measured soil-health improvement. The screen's lack of severe cold does not establish safety. No growth-duration model, soil lookup, pest screen, or forage-harvest validation. The transition interval is a user-adjustable planning assumption informed by general guidance.

## Honest conclusion
We have demonstrated the data pipeline, visual comparisons, evidence provenance, and changing assumptions. The next validation step is an agricultural review of an actual local rotation and cultivar-specific management requirements.
