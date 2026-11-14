"""Deterministic checks; no network or NASA account required."""
import unittest
from datetime import date
import server


def fixture():
    p = {k: {} for k in ('T2M', 'T2M_MIN', 'T2M_MAX', 'PRECTOTCORR')}
    for year in range(2015, 2025):
        for day, rain in ((1, 2), (2, 0), (3, 5)):
            key = f'{year}110{day}'
            for name, value in dict(T2M=10, T2M_MIN=-9 if day == 1 else 2,
                                    T2M_MAX=18, PRECTOTCORR=rain).items():
                p[name][key] = value
    return {'retrieved_at': '2026-11-13', 'data': {'header': {'fill_value': -999},
            'properties': {'parameter': p}}}


class WeatherMathTests(unittest.TestCase):
    def test_totals_counts_and_exclusive_end_date(self):
        result = server.summarize(date(2026, 11, 1), date(2026, 11, 4), fixture(), 'test')
        self.assertEqual(result['days'], 3)
        self.assertEqual(len(result['seasons']), 10)
        self.assertEqual(result['rain_median'], 7)
        self.assertEqual(result['freezing_median'], 1)
        self.assertEqual(result['cold_seasons'], 10)
        self.assertTrue(all(s['daily_rain'] == [2, 0, 5] for s in result['seasons']))

    def test_missing_observation_excludes_entire_season(self):
        data = fixture()
        data['data']['properties']['parameter']['T2M']['20151102'] = -999
        result = server.summarize(date(2026, 11, 1), date(2026, 11, 4), data, 'test')
        self.assertEqual(len(result['seasons']), 9)
        self.assertEqual(result['rain_median'], 7)

    def test_no_complete_season_is_an_error(self):
        with self.assertRaises(ValueError):
            server.summarize(date(2026, 12, 1), date(2026, 12, 4), fixture(), 'test')


if __name__ == '__main__':
    unittest.main()
