"""Field Window prototype. Python standard library only; no API keys."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import urlopen
from datetime import date, timedelta, datetime, timezone
import json
import statistics
import math

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / 'cache'
CACHE.mkdir(exist_ok=True)

def weather(lat, lon):
    # Fixed demonstration geography; avoid repeated requests within one area.
    if not (37.1 <= lat <= 37.6 and -120.8 <= lon <= -120.1):
        raise ValueError('This prototype supports the Merced demonstration area only.')
    path = CACHE / 'merced-power-2015-2024.json'
    params = dict(parameters='T2M,T2M_MIN,T2M_MAX,PRECTOTCORR', community='AG',
                  latitude=37.3022, longitude=-120.4830, start='20150101',
                  end='20241231', format='JSON', **{'time-standard': 'LST'})
    url = 'https://power.larc.nasa.gov/api/temporal/daily/point?' + urlencode(params)
    if path.exists():
        payload = json.loads(path.read_text(encoding='utf-8'))
    else:
        with urlopen(url, timeout=75) as response:
            raw = json.load(response)
        if 'parameter' not in raw.get('properties', {}):
            raise ValueError('NASA returned an unexpected response.')
        payload = dict(retrieved_at=datetime.now(timezone.utc).isoformat(), data=raw)
        path.write_text(json.dumps(payload), encoding='utf-8')
    return payload, url

def summarize(start, end, payload, url):
    # Map the month/day window onto ten historical seasons. Winter windows
    # use 2015–16 through 2023–24 to avoid incomplete endpoints.
    p = payload['data']['properties']['parameter']
    fill = payload['data'].get('header', {}).get('fill_value', -999)
    smd, emd = (start.month, start.day), (end.month, end.day)
    cross = emd < smd
    seasons = []
    monthly = {}
    for year in range(2015, 2024 if cross else 2025):
        try:
            a, b = date(year, *smd), date(year + int(cross), *emd)
        except ValueError:
            continue
        rows = []
        season_monthly = {}
        cursor = a
        while cursor < b:
            key = cursor.strftime('%Y%m%d')
            vals = {k: v.get(key) for k, v in p.items()}
            if all(isinstance(vals.get(k), (float, int)) and math.isfinite(vals[k]) and vals[k] != fill
                   for k in ('T2M', 'T2M_MIN', 'T2M_MAX', 'PRECTOTCORR')):
                rows.append(vals)
                bucket = season_monthly.setdefault(cursor.month, [])
                bucket.append(vals)
            cursor += timedelta(days=1)
        expected = (b-a).days
        if expected and len(rows) == expected:
            for month, values in season_monthly.items():
                monthly.setdefault(month, []).extend(values)
            seasons.append(dict(label=f'{year}–{str(year+1)[2:]}' if cross else str(year),
                                rain=round(sum(r['PRECTOTCORR'] for r in rows),1),
                                freezing=sum(r['T2M_MIN'] <= 0 for r in rows),
                                hot=sum(r['T2M_MAX'] >= 35 for r in rows),
                                severe_cold=sum(r['T2M_MIN'] <= -8 for r in rows),
                                daily_rain=[round(r['PRECTOTCORR'], 3) for r in rows],
                                mean=round(statistics.mean(r['T2M'] for r in rows),1)))
    if not seasons:
        raise ValueError('No complete historical seasons available for these dates.')
    days = (end-start).days
    order = list(dict.fromkeys((start + timedelta(days=i)).month for i in range(days)))
    return dict(days=days, seasons=seasons, cold_seasons=sum(s['severe_cold'] > 0 for s in seasons),
                rain_median=round(statistics.median(s['rain'] for s in seasons),1),
                rain_min=min(s['rain'] for s in seasons), rain_max=max(s['rain'] for s in seasons),
                freezing_median=statistics.median(s['freezing'] for s in seasons),
                hot_median=statistics.median(s['hot'] for s in seasons),
                monthly=[dict(month=m, mean=round(statistics.mean(r['T2M'] for r in monthly[m]),1)) for m in order if m in monthly],
                source_url=url, retrieved_at=payload['retrieved_at'],
                parameters=payload['data'].get('parameters', {}),
                data_period='2015–2024', point=dict(latitude=37.3022,longitude=-120.4830))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != '/api/weather':
            # Do not serve Python source or internal cache through the app.
            if parsed.path not in ('/', '/index.html', '/app.js', '/style.css', '/catalog.json', '/favicon.ico'):
                self.send_error(404)
                return
            return super().do_GET()
        try:
            q = parse_qs(parsed.query)
            a, b = date.fromisoformat(q['start'][0]), date.fromisoformat(q['end'][0])
            if not 1 <= (b-a).days <= 365:
                raise ValueError('Choose a window between 1 and 365 days.')
            payload, url = weather(37.3022, -120.4830)
            result = summarize(a,b,payload,url)
            status = 200
        except (ValueError, KeyError) as exc:
            status, result = 400, {'error': str(exc)}
        except Exception:
            status, result = 503, {'error': 'NASA POWER is unavailable and no saved data exists yet. Try again shortly. No weather values have been invented.'}
        raw = json.dumps(result, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

if __name__ == '__main__':
    print('Field Window: http://127.0.0.1:8765', flush=True)
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
