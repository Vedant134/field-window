"""Pure historical-season calculations for Field Window.

No network, files, or clock access: every function maps inputs to outputs,
so the arithmetic can be unit-tested without NASA being reachable.

Methods
- Reference evapotranspiration: Hargreaves equation, FAO Irrigation and
  Drainage Paper 56 (Allen et al., 1998), eq. 52, with extraterrestrial
  radiation from eq. 21-25. It needs only daily min/max temperature and
  latitude. It describes atmospheric demand over a reference grass surface;
  it is not the water use of any particular crop.
- Wet day: at least 1 mm of precipitation (WMO climatological convention).
"""
from datetime import date, timedelta
import math
import statistics

FIRST_YEAR, LAST_YEAR = 1995, 2024          # 30 calendar years of daily records
REQUIRED = ('T2M', 'T2M_MIN', 'T2M_MAX', 'PRECTOTCORR')
OPTIONAL = ('GWETROOT',)                    # modelled root-zone wetness, 0-1
WET_DAY_MM = 1.0
EDGE_DAYS = 14                              # opening / closing fortnight
RECENT_SEASONS = 10


def extraterrestrial_radiation(latitude, day_of_year):
    """Daily extraterrestrial radiation Ra in MJ m-2 day-1 (FAO-56 eq. 21)."""
    phi = math.radians(latitude)
    dr = 1 + 0.033 * math.cos(2 * math.pi * day_of_year / 365)
    delta = 0.409 * math.sin(2 * math.pi * day_of_year / 365 - 1.39)
    # Clamp so polar day and polar night give a defined sunset hour angle.
    ws = math.acos(max(-1.0, min(1.0, -math.tan(phi) * math.tan(delta))))
    ra = (24 * 60 / math.pi) * 0.0820 * dr * (
        ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws))
    return max(0.0, ra)


def reference_et(tmin, tmax, ra):
    """Hargreaves reference evapotranspiration in mm/day (FAO-56 eq. 52)."""
    spread = max(0.0, tmax - tmin)
    return max(0.0, 0.0023 * ((tmax + tmin) / 2 + 17.8) * math.sqrt(spread) * 0.408 * ra)


def anchored(year, month, day):
    """Month/day in a given year; 29 February falls back to 28 February."""
    try:
        return date(year, month, day)
    except ValueError:
        return date(year, month, 28)


def _valid(value, fill):
    return isinstance(value, (int, float)) and not isinstance(value, bool) \
        and math.isfinite(value) and value != fill


def _spread(values, digits=1):
    """Median, quartiles, and extremes of a list of season values."""
    values = sorted(values)
    if not values:
        return None
    if len(values) >= 2:
        q1, _, q3 = statistics.quantiles(values, n=4, method='inclusive')
    else:
        q1 = q3 = values[0]
    r = lambda v: round(v, digits)
    return dict(median=r(statistics.median(values)), q1=r(q1), q3=r(q3),
                min=r(values[0]), max=r(values[-1]), n=len(values))


def _longest_dry_run(rain):
    best = run = 0
    for value in rain:
        run = run + 1 if value < WET_DAY_MM else 0
        best = max(best, run)
    return best


def growing_period(rows, transition):
    """Per-season evidence for the days before the reserved transition."""
    rows = rows[:max(0, len(rows) - transition)]
    if not rows:
        return None
    rain = [r['PRECTOTCORR'] for r in rows]
    demand = sum(r['et0'] for r in rows)
    opening, closing = rain[:EDGE_DAYS], rain[-EDGE_DAYS:]
    first_wet = next((i for i, v in enumerate(rain) if v >= WET_DAY_MM), None)
    return dict(rain=round(sum(rain), 1), demand=round(demand, 1),
                balance=round(sum(rain) - demand, 1),
                share=round(100 * sum(rain) / demand) if demand > 0 else None,
                opening_wet_days=sum(v >= WET_DAY_MM for v in opening),
                closing_wet_days=sum(v >= WET_DAY_MM for v in closing),
                closing_rain=round(sum(closing), 1),
                days_to_first_rain=first_wet,
                longest_dry_run=_longest_dry_run(rain))


def summarize(start, end, payload, url, lat=37.3022, lon=-120.4830, transition=0):
    """Map the month/day window onto every complete historical season.

    Whole-window fields describe the full gap. The `growing` block describes
    the days left after reserving `transition` days before the next crop.
    A season with any missing required observation is excluded entirely.
    """
    p = payload['data']['properties']['parameter']
    fill = payload['data'].get('header', {}).get('fill_value', -999)
    smd, emd = (start.month, start.day), (end.month, end.day)
    cross = emd <= smd
    days = (end - start).days
    transition = max(0, int(transition))
    seasons, monthly = [], {}
    for year in range(FIRST_YEAR, LAST_YEAR + (0 if cross else 1)):
        a, b = anchored(year, *smd), anchored(year + int(cross), *emd)
        rows, season_monthly, complete = [], {}, True
        cursor = a
        while cursor < b:
            key = cursor.strftime('%Y%m%d')
            vals = {k: p.get(k, {}).get(key) for k in REQUIRED + OPTIONAL}
            if not all(_valid(vals[k], fill) for k in REQUIRED):
                complete = False
                break
            vals['et0'] = reference_et(vals['T2M_MIN'], vals['T2M_MAX'],
                                       extraterrestrial_radiation(lat, cursor.timetuple().tm_yday))
            rows.append(vals)
            season_monthly.setdefault(cursor.month, []).append(vals)
            cursor += timedelta(days=1)
        if not complete or not rows:
            continue
        for month, values in season_monthly.items():
            monthly.setdefault(month, []).extend(values)
        soil = rows[0].get('GWETROOT')
        seasons.append(dict(
            label=f'{year}–{str(year + 1)[2:]}' if cross else str(year),
            rain=round(sum(r['PRECTOTCORR'] for r in rows), 1),
            demand=round(sum(r['et0'] for r in rows), 1),
            freezing=sum(r['T2M_MIN'] <= 0 for r in rows),
            hot=sum(r['T2M_MAX'] >= 35 for r in rows),
            severe_cold=sum(r['T2M_MIN'] <= -8 for r in rows),
            daily_rain=[round(r['PRECTOTCORR'], 3) for r in rows],
            mean=round(statistics.mean(r['T2M'] for r in rows), 1),
            soil_wetness_start=round(soil, 2) if _valid(soil, fill) else None,
            growing=growing_period(rows, transition)))
    if not seasons:
        raise ValueError('No complete historical seasons available for these dates.')
    order = list(dict.fromkeys((start + timedelta(days=i)).month for i in range(days)))
    grown = [s['growing'] for s in seasons if s['growing']]
    growing = None
    if grown:
        recent = grown[-RECENT_SEASONS:]
        shares = [g['share'] for g in grown if g['share'] is not None]
        waits = [g['days_to_first_rain'] for g in grown if g['days_to_first_rain'] is not None]
        growing = dict(
            days=days - transition, seasons=len(grown),
            rain=_spread([g['rain'] for g in grown]),
            demand=_spread([g['demand'] for g in grown]),
            share=_spread(shares, 0),
            seasons_rain_met_demand=sum(g['balance'] >= 0 for g in grown),
            seasons_rain_under_half_demand=sum(s < 50 for s in shares),
            closing_wet_days=_spread([g['closing_wet_days'] for g in grown]),
            seasons_dry_closing=sum(g['closing_wet_days'] == 0 for g in grown),
            opening_wet_days=_spread([g['opening_wet_days'] for g in grown]),
            seasons_dry_opening=sum(g['opening_wet_days'] == 0 for g in grown),
            days_to_first_rain=_spread(waits, 0),
            longest_dry_run=_spread([g['longest_dry_run'] for g in grown], 0),
            recent=dict(seasons=len(recent),
                        rain_median=round(statistics.median(g['rain'] for g in recent), 1),
                        demand_median=round(statistics.median(g['demand'] for g in recent), 1)),
            edge_days=min(EDGE_DAYS, days - transition), wet_day_mm=WET_DAY_MM)
    soil_values = [s['soil_wetness_start'] for s in seasons if s['soil_wetness_start'] is not None]
    scoped = 37.1 <= lat <= 37.6 and -120.8 <= lon <= -120.1
    return dict(
        days=days, transition_days=transition, seasons=seasons,
        cold_seasons=sum(s['severe_cold'] > 0 for s in seasons),
        rain_median=round(statistics.median(s['rain'] for s in seasons), 1),
        rain_min=min(s['rain'] for s in seasons), rain_max=max(s['rain'] for s in seasons),
        rain=_spread([s['rain'] for s in seasons]),
        freezing_median=statistics.median(s['freezing'] for s in seasons),
        hot_median=statistics.median(s['hot'] for s in seasons),
        soil_wetness_start=_spread(soil_values, 2),
        growing=growing,
        monthly=[dict(month=m, mean=round(statistics.mean(r['T2M'] for r in monthly[m]), 1))
                 for m in order if m in monthly],
        source_url=url, retrieved_at=payload['retrieved_at'],
        parameters=payload['data'].get('parameters', {}),
        data_period=f'{FIRST_YEAR}–{LAST_YEAR}', point=dict(latitude=lat, longitude=lon),
        methods=dict(reference_et='Hargreaves (FAO-56 eq. 52), from daily min/max temperature and latitude',
                     wet_day=f'at least {WET_DAY_MM:g} mm precipitation',
                     soil_wetness='MERRA-2 modelled root-zone wetness (0–1) on the first day; not a field measurement'),
        crop_guidance_scope='merced_example' if scoped else 'unavailable')
