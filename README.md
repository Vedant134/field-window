# Field Window — decision-support prototype

Start with [the project overview](PROJECT.md) for the purpose, UI, resources, method, and judge-facing decisions and tradeoffs. This is the main project document. See [the math](MATH.md) for calculations and [the judge walkthrough](JUDGE-WALKTHROUGH.md) for demonstration notes.

Run verification with `python -m unittest -v` and `node --check app.js`. GitHub Actions repeats these checks on pushes and pull requests. Keep `main` working; teammates can use short feature branches and pull requests. A saved public NASA response is included for a reproducible offline demonstration; it contains regional environmental records, not private farmer inputs.

## Run
Requires Python 3.10 or later, no additional packages or API key.
Double-click Start.bat, then open http://127.0.0.1:8765. Keep the terminal open.
Alternatively run `python server.py` in this directory. The active server may already be running.

## Scope
Worldwide city search or coordinates select the NASA POWER request location. Merced remains the test case for crop guidance: existing gap management versus oats managed for cover or forage. Outside the Merced test area, strategies are generic and marked as needing regional crop guidance; California planting calendars are not applied. Two management alternatives of the same species make the tradeoffs visible without pretending weather alone selects a different crop. This is a researched scenario, not a locally validated rotation or planting recommendation. Previous and next crop species are not specified or screened for compatibility.

## Working features
- Worldwide city search (Open-Meteo Geocoding / GeoNames), coordinate fallback, and location-specific cached NASA POWER daily data, 1995–2024.
- Dates, baseline, irrigation category; browser-local input persistence.
- Seasonal rainfall distributions and cumulative curves for selected dry, middle-ranked, and wet seasons.
- Historical freezing context and a literature-based oat cold-exposure screen; not predicted injury or survival.
- Rain against atmospheric demand (FAO-56 Hargreaves reference evapotranspiration) per past season, plus wet-day counts for the first and last 14 growing days. These recalculate when the transition days change.
- Three comparison cards with reasons and uncertainties; the forage and cover cards read the closing fortnight differently.
- Soil-cover versus feed-use goal switch; this changes goal alignment, not measured agronomic superiority.
- Visual calendar and an adjustable transition interval, supported by general California guidance.
- Printable results and downloadable JSON including evidence and assumptions.

## What changed from the first prototype
Removed invented 90/120-day minimum growing periods and the broad 5–25°C monthly-mean suitability screen. A shorter growing window does not automatically mean failure unless the transition allowance leaves no growing time. Biomass and forage readiness are explicitly unknown. The default 20-day transition setting is an editable scenario choice within UC ANR's general 10–30-day guidance; it is not a validated oat or forage requirement.

## Data-science method
Historical seasonal time-series analysis plus transparent constraint screening and sensitivity analysis. No machine learning or forecasting.
1. Retrieve temperature and precipitation; preserve units and provenance.
2. Reject incomplete seasons and missing observations.
3. Extract the same month/day interval in each historical year.
4. Calculate rainfall totals, medians/ranges, cumulative rainfall, and temperature exposure counts.
5. Compare start month with sourced winter-oat guidance; report exposure and missing evidence.
6. Show how calendar allocation changes as the transition assumption changes.
Do not interpret the historical count as a future success probability.

## Architecture
index.html and style.css: UI.
app.js: scenarios, goal alignment, timelines, chart rendering, and export.
catalog.json: compact crop evidence and provenance.
analysis.py: pure historical calculations (season selection, reference evapotranspiration, wet-day counts); no network or file access.
server.py: standard-library web server, NASA API/cache.
test_analysis.py, test_server.py: unit tests, including a published FAO-56 worked example.
cache/merced-power-1995-2024.json: real downloaded response; preserve for offline demonstrations.

New location caches are ignored by Git to avoid publishing user-selected coordinates. The original public Merced sample remains tracked for reproducibility. NASA weather is gridded regional context, not a sensor on the field. Windows crossing New Year use 29 complete seasons. Other windows may use 30. End dates are excluded; a 29 February endpoint falls back to 28 February. Chart labels use rounded seasonal totals; cumulative curves sum daily observations. Rainfall cannot establish irrigation sufficiency.

## Demonstration
1. Confirm dates and current practice; click Explore my options.
2. Show variation in seasonal precipitation.
3. Open When did the rain arrive? Explain why timing differs from totals.
4. Compare current practice, oats for cover, and oats for forage.
5. Switch between soil cover and feed use. Explain why a goal match is not proof of suitability.
6. Open the transition assumption; increase from 20 to 30 days. Growing time decreases by ten days, the timeline updates, and the rain-against-demand and closing-fortnight counts recalculate.
7. Open Why this result? and the sources.
8. Name the remaining uncertainties instead of claiming yield, profit, water savings, or measured soil benefits.

## Before judging
- Review one actual local crop sequence and next-crop compatibility with a farmer or agricultural mentor.
- Confirm cultivar, establishment, termination and forage harvest timing, soil/pest concerns, and equipment.
- Integrate those verified requirements rather than inventing maturity thresholds.
- Document reviewer corrections and the scope of validation.
- Soil maps, crop-history autofill, OpenET, and imagery are deferred.

## Sources
NASA POWER: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
UC SAREP oat profile: https://sarep.ucdavis.edu/covercrop/oat
UC ANR California annual rotation considerations: https://ucanr.edu/sites/default/files/2024-09/402186.pdf
Challenge: https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=resources
The oat profile compiles older literature. Its general guidance must be reviewed for current local cultivars and conditions. The sources do not validate our prototype as a farm recommendation system.

## Global support boundary
Weather access works by worldwide latitude/longitude where POWER has the requested data. City selection is a regional point, not a field boundary. A location without regional crop evidence receives weather context and generic scenarios, not a locally validated recommendation. Open-Meteo supplies coordinates only; NASA remains the sole weather provider. Geocoding attribution: https://open-meteo.com/en/docs/geocoding-api
