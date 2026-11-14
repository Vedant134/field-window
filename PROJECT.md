# Field Window — Project Overview

## What we are building

**An interactive decision-support website with charts and a calendar.**

It is designed for farmers worldwide. Merced is our initial test case, not the geographic limit. It helps a farmer compare what to do between harvesting one crop and planting the next. “Decision support” is the purpose. “Interactive” means results respond when the farmer changes inputs. Charts and the calendar explain the results. An interactive map is not part of this version.

## The problem and the value

A farmer can keep their existing practice or plant something during the break. An extra crop may provide plant cover or animal feed, but it also needs water, time, and management.

We bring the dates, weather history, and crop guidance together so the farmer can see the tradeoffs in one place. We help them decide what deserves further investigation; we do not select a guaranteed best crop.

This addresses Field Shift’s goal: use NASA environmental information to help farmers explore crop-rotation choices, explain tradeoffs, and make uncertainty visible.

## The UI, step by step

### 1. Your situation

Start with a city search that works worldwide, plus a coordinate option for rural locations. Merced is prefilled only as a demonstration. After choosing a location, ask:

- What do you currently do during the break: keep crop residue or leave it without planted cover?
- When is the field available, and when must the next crop start?
- Can you irrigate an additional crop: rainfall only, some irrigation, or unsure?

Use one button: **Explore my options**. Save answers in the browser. City selection supplies coordinates for the NASA request; the selected city and country are confirmed before analysis. Coordinates can identify places outside cities. No automatic farm detection or field map is implemented.

### 2. Your comparison

Show three cards:

| Choice | What it means |
| --- | --- |
| Current approach | Continue the practice the farmer selected. |
| Oats for soil cover | Grow oats mainly to cover the ground, then remove them before the next crop. |
| Oats for animal feed | Explore growing oats to harvest for animals. Harvest readiness must be confirmed. |

These named oat scenarios appear only in the Merced test area. Elsewhere, show the current approach plus generic cover-crop and animal-feed scenarios labeled “Local crop guidance needed.” Do not apply California planting months or recommend oats worldwide. The current Merced scenarios compare two uses of the same species. They are not yet a locally validated crop rotation. Previous and next crop species are not collected or checked.

Each card explains calendar constraints, potential benefits, water questions, work required, and unknowns. A soil-cover/feed-use switch changes which goal an option matches; it does not prove that option is better.

### 3. Understand the evidence

- Rainfall bars show how the same calendar window differed across about 30 past seasons.
- A rain-against-demand chart shows, season by season, whether rain in the growing days matched atmospheric demand (reference evapotranspiration).
- Three headline counts recalculate when the transition days change: seasons where rain met demand, wet days in the last 14 growing days, and the wait for the first rain.
- An expandable cumulative chart shows when rain arrived in selected dry, middle, and wet seasons.
- A calendar shows available growing time and reserved transition time before the next crop.
- “Why this result?” exposes checks, sources, and uncertainty.
- Print or download the comparison.

## Resources: exactly what each does

| Resource | Implementation | Contribution |
| --- | --- | --- |
| NASA POWER | Python requests daily rainfall, temperatures, and modelled root-zone wetness (1995–2024) through the API, then saves the response. | Historical growing conditions at the selected worldwide coordinates, subject to NASA data availability. |
| UC SAREP oat profile | Manually reviewed guidance stored in the crop reference file. | Broad planting-month guidance and a cold-exposure reference; not a growth model. |
| UC ANR California guidance | Manually reviewed management information. | General transition guidance and management context. |
| Open-Meteo Geocoding / GeoNames | City search API converts a place name into selectable coordinates. It supplies no weather. | Keeps worldwide location entry simple. Coordinates remain a fallback. |
| FAO Irrigation and Drainage Paper 56 | Hargreaves equation implemented in `analysis.py` and checked against a published worked example. | Reference evapotranspiration from temperature and latitude: atmospheric demand, not crop water use. |
| Farmer inputs | Short form, saved locally in their browser. | Dates, existing practice, and irrigation category. |

POWER is our only environmental-data service. Soil maps, SMAP, GPM, Landsat, ECOSTRESS, OpenET, and crop-history maps are deferred.

## Data method and architecture

**City search or coordinates → NASA records for that location → historical calculations → region-scoped checks → visual comparison.**

Weather retrieval is global; agricultural evidence is regional. Each crop catalog must identify its geographic and seasonal scope. Where no suitable catalog exists, report that gap and keep the results exploratory. Do not assume that northern and southern hemispheres share planting months. Cache records by location and request settings; never substitute Merced data for another place.

1. Clean records: check units and exclude incomplete historical seasons.
2. Extract the farmer’s calendar window from each past year.
3. Sum precipitation, calculate its median, quartiles, and range, and count temperature events.
4. For the growing days left after the transition: compare rain with reference evapotranspiration, count wet days (at least 1 mm) in the first and last 14 days, and measure the wait for the first rain. Report each as “k of n past seasons.”
5. Compare start month with sourced guidance; subtract reserved transition days.
6. Explain the result and report what cannot be established.

This is **historical seasonal analysis and transparent requirement checks**. Changing an assumption and recalculating is **sensitivity analysis**.

The 1995–2024 archive (30 calendar years, the usual length of a climate reference period) is a historical comparison period, not training data. We do not forecast weather or train machine learning. Automatically searching for the best planting dates is not implemented or required for this baseline.

## Decisions and tradeoffs we explain to judges

| Decision | Why we chose it | Limitation we accept |
| --- | --- | --- |
| Global location selection; one regional crop example | Farmers can examine local weather while we validate agricultural evidence in stages. | Weather is location-specific, but crop guidance is not yet worldwide. |
| POWER plus agricultural references | Connects environmental history with documented plant guidance. | No direct soil-moisture or field-condition measurement. |
| Rain compared with reference evapotranspiration | Uses only data already downloaded and a published FAO method; works at any latitude. | Demand is for a reference grass surface. No crop coefficient, soil storage, or irrigation is modelled, so it is not a crop water requirement. |
| Explicit checks instead of trained AI | Every result can be explained; we lack labeled farm-outcome data. | No learned yield or crop-success prediction. |
| Few farmer questions | Reduces setup effort. | Equipment, soil, pest, and crop compatibility remain unknown. |
| Comparisons instead of a best-crop score | Keeps farmer priorities and uncertainty visible. | No claim of a mathematically optimal choice. |

## What is working and what comes next

**Working:** worldwide city search and coordinate input, location-specific NASA download/cache, historical calculations over 30 years (rain against demand, establishment and closing-fortnight wetness), input persistence, three scenario cards, goal switch, charts, calendar adjustment, source explanations, print/export, and calculation tests.

**Next:** expand regional crop catalogs with documented local requirements; confirm a real local crop sequence; review whether the two alternatives are useful; add documented management and growth requirements where supported; test the results with an agricultural reviewer and a first-time user.

**Known weakness:** both oat scenarios face the same weather over the same dates. The cards now differ in one evidence-based way: the forage card reads closing-fortnight wetness as a harvest and drying risk, the cover card as a termination-access question. Weather still does not establish which choice is superior, and no sourced growth-duration or heat-unit requirement is available to say whether forage would be ready. Finding that requirement is more valuable than adding datasets or decoration.

**Data caution:** NASA POWER precipitation is a regional grid value (about half a degree). For the Merced sample it reports a median of about 307 mm for 15 October–1 March, which looks high for the valley floor; compare it with a local gauge before relying on the rain totals.

We do not claim sufficient irrigation, crop maturity, yield, profit, measured erosion reduction, or measured soil improvement. The adjustable transition interval is a planning assumption informed by general guidance, not a universal crop requirement.

## Judge explanation and demonstration

“We built an interactive tool that combines NASA weather history with agricultural guidance to compare what a farmer could do between two crops. It shows the time available, historical weather concerns, management tradeoffs, and missing information.”

Demonstrate: enter dates → show historical weather → compare three cards → change transition time → show the calendar update → open the evidence → state what still needs agricultural validation.

## Sources

- [Field Shift challenge](https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/)
- [Open-Meteo Geocoding / GeoNames attribution](https://open-meteo.com/en/docs/geocoding-api)
- [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [FAO Irrigation and Drainage Paper 56: reference evapotranspiration](https://www.fao.org/4/x0490e/x0490e00.htm)
- [UC SAREP oat profile](https://sarep.ucdavis.edu/covercrop/oat)
- [UC ANR California crop-rotation considerations](https://ucanr.edu/sites/default/files/2024-09/402186.pdf)
