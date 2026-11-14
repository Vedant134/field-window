"""Checks for the pure calculations in analysis.py; no network required."""
import unittest
from datetime import date
import analysis


def payload(years=range(1995, 2025), month=11, rain=(2, 0, 5, 0, 0, 1), tmin=5, tmax=20, extra=None):
    p = {k: {} for k in analysis.REQUIRED}
    for year in years:
        for i, value in enumerate(rain):
            key = f'{year}{month:02d}{i + 1:02d}'
            p['T2M'][key], p['T2M_MIN'][key], p['T2M_MAX'][key] = (tmin + tmax) / 2, tmin, tmax
            p['PRECTOTCORR'][key] = value
    p.update(extra or {})
    return {'retrieved_at': '2026-11-14', 'data': {'header': {'fill_value': -999},
            'properties': {'parameter': p}}}


def run(transition=0, data=None, lat=37.3, end_day=7):
    return analysis.summarize(date(2026, 11, 1), date(2026, 11, end_day), data or payload(),
                              'test', lat, -120.5, transition)


class ReferenceEvapotranspirationTests(unittest.TestCase):
    def test_extraterrestrial_radiation_matches_fao56_example_8(self):
        # FAO-56 example 8: 20°S on 3 September (day 246) gives 32.2 MJ m-2 day-1.
        self.assertAlmostEqual(analysis.extraterrestrial_radiation(-20, 246), 32.2, delta=0.1)

    def test_radiation_is_defined_and_non_negative_at_the_poles(self):
        self.assertEqual(analysis.extraterrestrial_radiation(90, 355), 0)
        self.assertGreater(analysis.extraterrestrial_radiation(90, 172), 40)
        self.assertGreater(analysis.extraterrestrial_radiation(-90, 355), 40)

    def test_hargreaves_hand_calculation(self):
        # 0.0023 * (20 + 17.8) * sqrt(10) * 0.408 * 30 = 3.365 mm/day
        self.assertAlmostEqual(analysis.reference_et(15, 25, 30), 3.365, places=3)

    def test_demand_is_never_negative(self):
        self.assertEqual(analysis.reference_et(-40, -30, 10), 0)
        self.assertEqual(analysis.reference_et(12, 10, 30), 0)  # inverted inputs

    def test_hemispheres_get_opposite_seasons(self):
        north, south = run(lat=40), run(lat=-40)
        self.assertGreater(south['seasons'][0]['demand'], 2 * north['seasons'][0]['demand'])


class GrowingPeriodTests(unittest.TestCase):
    def test_transition_removes_days_from_the_end(self):
        result = run(transition=2)
        self.assertEqual(result['growing']['days'], 4)
        self.assertEqual(result['growing']['rain']['median'], 7)       # 2+0+5+0
        self.assertEqual(result['rain']['median'], 8)                   # whole window unchanged
        self.assertEqual(result['seasons'][0]['growing']['closing_wet_days'], 2)

    def test_wet_days_and_dry_runs(self):
        g = run()['seasons'][0]['growing']
        self.assertEqual(g['opening_wet_days'], 3)      # 2, 5 and exactly 1 mm count
        self.assertEqual(g['days_to_first_rain'], 0)
        self.assertEqual(g['longest_dry_run'], 2)

    def test_season_without_rain_reports_no_first_rain_day(self):
        result = run(data=payload(rain=(0, 0.9, 0, 0, 0, 0)))
        g = result['seasons'][0]['growing']
        self.assertIsNone(g['days_to_first_rain'])
        self.assertEqual(g['longest_dry_run'], 6)
        self.assertEqual(result['growing']['seasons_dry_opening'], 30)
        self.assertIsNone(result['growing']['days_to_first_rain'])

    def test_balance_counts_seasons_where_rain_met_demand(self):
        wet = run(data=payload(rain=(40,) * 6))['growing']
        dry = run(data=payload(rain=(0,) * 6))['growing']
        self.assertEqual(wet['seasons_rain_met_demand'], 30)
        self.assertEqual(dry['seasons_rain_met_demand'], 0)
        self.assertEqual(dry['seasons_rain_under_half_demand'], 30)

    def test_transition_longer_than_window_leaves_no_growing_period(self):
        result = run(transition=10)
        self.assertIsNone(result['growing'])
        self.assertEqual(len(result['seasons']), 30)

    def test_recent_seasons_are_the_last_ten(self):
        data = payload()
        for year in range(2015, 2025):
            data['data']['properties']['parameter']['PRECTOTCORR'][f'{year}1101'] = 12
        g = run(data=data)['growing']
        self.assertEqual(g['recent'], dict(seasons=10, rain_median=18, demand_median=g['recent']['demand_median']))
        self.assertEqual(g['rain']['median'], 8)


class SeasonSelectionTests(unittest.TestCase):
    def test_thirty_seasons_and_quartiles(self):
        result = run()
        self.assertEqual(result['rain']['n'], 30)
        self.assertEqual(result['data_period'], '1995–2024')

    def test_optional_soil_wetness_never_excludes_a_season(self):
        soil = {'GWETROOT': {f'{y}1101': (0.5 if y != 2000 else -999) for y in range(1995, 2025)}}
        result = run(data=payload(extra=soil))
        self.assertEqual(len(result['seasons']), 30)
        self.assertEqual(result['soil_wetness_start']['n'], 29)
        self.assertEqual(result['soil_wetness_start']['median'], 0.5)

    def test_leap_day_start_falls_back_to_28_february(self):
        self.assertEqual(analysis.anchored(2023, 2, 29), date(2023, 2, 28))
        self.assertEqual(analysis.anchored(2024, 2, 29), date(2024, 2, 29))

    def test_window_crossing_new_year_uses_consecutive_years(self):
        p = payload(month=12, rain=(1,) * 31)
        jan = payload(month=1, rain=(1,) * 31)
        for name in analysis.REQUIRED:
            p['data']['properties']['parameter'][name].update(jan['data']['properties']['parameter'][name])
        result = analysis.summarize(date(2026, 12, 20), date(2027, 1, 10), p, 'test', 37.3, -120.5)
        self.assertEqual(len(result['seasons']), 29)
        self.assertEqual(result['seasons'][0]['label'], '1995–96')
        self.assertEqual(result['seasons'][0]['rain'], 21)


if __name__ == '__main__':
    unittest.main()
