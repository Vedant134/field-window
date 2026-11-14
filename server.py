"""Field Window prototype. Python standard library only; no API keys."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import urlopen
from datetime import date, datetime, timezone
import json
import math
from functools import lru_cache
from hashlib import sha256
import analysis


def coordinates(lat, lon):
    lat, lon = float(lat), float(lon)
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('Latitude must be −90 to 90 and longitude −180 to 180.')
    return round(lat, 4), round(lon, 4)


@lru_cache(maxsize=100)
def search_places(query):
    if not 2 <= len(query) <= 120:
        raise ValueError('Enter a city name between 2 and 120 characters.')
    url = 'https://geocoding-api.open-meteo.com/v1/search?' + urlencode(
        dict(name=query, count=8, language='en', format='json'))
    with urlopen(url, timeout=20) as response:
        data = json.load(response)
    return [dict(label=', '.join(filter(None, [r['name'], r.get('admin1'), r.get('country')])),
                 latitude=r['latitude'], longitude=r['longitude'])
            for r in data.get('results', [])]

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / 'cache'
CACHE.mkdir(exist_ok=True)

PARAMETERS = 'T2M,T2M_MIN,T2M_MAX,PRECTOTCORR,GWETROOT'
SAMPLE = (37.3022, -120.483)


def power_url(lat, lon):
    params = dict(parameters=PARAMETERS, community='AG', latitude=lat, longitude=lon,
                  start=f'{analysis.FIRST_YEAR}0101', end=f'{analysis.LAST_YEAR}1231',
                  format='JSON', **{'time-standard': 'LST'})
    return 'https://power.larc.nasa.gov/api/temporal/daily/point?' + urlencode(params)


@lru_cache(maxsize=8)
def _load(path, modified):
    # Keyed by modification time so a rewritten cache file is re-read.
    return json.loads(Path(path).read_text(encoding='utf-8'))


def weather(lat, lon):
    lat, lon = coordinates(lat, lon)
    url = power_url(lat, lon)
    # Cache by complete request identity; never reuse Merced observations elsewhere.
    path = CACHE / ('power-' + sha256(url.encode()).hexdigest()[:20] + '.json')
    sample = CACHE / f'merced-power-{analysis.FIRST_YEAR}-{analysis.LAST_YEAR}.json'
    if (lat, lon) == SAMPLE and not path.exists() and sample.exists():
        path = sample
    if path.exists():
        try:
            return _load(str(path), path.stat().st_mtime_ns), url
        except (OSError, ValueError):
            pass  # unreadable cache: fall through and download again
    with urlopen(url, timeout=75) as response:
        raw = json.load(response)
    if 'parameter' not in raw.get('properties', {}):
        raise ValueError('NASA returned an unexpected response.')
    payload = dict(retrieved_at=datetime.now(timezone.utc).isoformat(), data=raw)
    if path == sample:
        path = CACHE / ('power-' + sha256(url.encode()).hexdigest()[:20] + '.json')
    # Write then rename, so an interrupted download never leaves a half-written cache.
    partial = path.with_suffix('.part')
    partial.write_text(json.dumps(payload), encoding='utf-8')
    partial.replace(path)
    return payload, url


summarize = analysis.summarize

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path not in ('/api/weather', '/api/places'):
            # Do not serve Python source or internal cache through the app.
            if parsed.path not in ('/', '/index.html', '/app.js', '/style.css', '/catalog.json', '/favicon.ico'):
                self.send_error(404)
                return
            return super().do_GET()
        try:
            q = parse_qs(parsed.query)
            if parsed.path == '/api/places':
                result = dict(results=search_places(q.get('q', [''])[0].strip()))
            else:
                lat, lon = coordinates(q.get('lat', ['37.3022'])[0], q.get('lon', ['-120.4830'])[0])
                a, b = date.fromisoformat(q['start'][0]), date.fromisoformat(q['end'][0])
                if not 1 <= (b-a).days <= 365:
                    raise ValueError('Choose a window between 1 and 365 days.')
                raw_transition = q.get('transition', ['0'])[0]
                transition = int(raw_transition) if raw_transition.isdigit() else -1
                if not 0 <= transition <= 365:
                    raise ValueError('Transition days must be between 0 and 365.')
                payload, url = weather(lat, lon)
                result = summarize(a, b, payload, url, lat, lon, transition)
            status = 200
        except (ValueError, KeyError) as exc:
            status, result = 400, {'error': str(exc)}
        except Exception:
            message = 'City search is unavailable. Try coordinates instead.' if parsed.path == '/api/places' else 'NASA POWER is unavailable for this location and no usable saved response could be loaded. Try again shortly. No weather values have been invented.'
            status, result = 503, {'error': message}
        raw = json.dumps(result, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

if __name__ == '__main__':
    print('Field Window: http://127.0.0.1:8765', flush=True)
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
