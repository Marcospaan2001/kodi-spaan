import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('sport_sources', Path(__file__).resolve().parents[1] / 'video-mod/sport_sources.py')
sport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sport)

FAWA = '''<div class="user-item --active"><a href="match.html">
<div class="user-item__name">Ajax vs PSV</div><div class="user-item__playing">Eredivisie 20:00</div>
<div class="user-item --active"><a href="basket.html"><div class="user-item__name">NBA</div><div class="user-item__playing">Basketball</div>'''


class Sports(unittest.TestCase):
    def test_sports_do_not_mix(self):
        self.assertEqual(sport.sport_for('Formula 1 qualifying'), 'Formule 1')
        self.assertEqual(sport.sport_for('PDC World Championship'), 'Darts')
        self.assertIsNone(sport.sport_for('NFL Football'))
        rows = sport.parse_fawa(FAWA)
        self.assertEqual([r['title'] for r in rows], ['Ajax vs PSV'])

    def test_new_cdn_array_and_html_entities(self):
        page = '''var S1=["https://cdn1.example/hls/","https://cdn2.example/hls/"];var S2="match";var S3=".m3u8";'''
        self.assertEqual(sport.direct_links(page, 'https://example.org/'), ['https://cdn1.example/hls/match.m3u8', 'https://cdn2.example/hls/match.m3u8'])
        self.assertEqual(sport.direct_links('"https://example.org/a.m3u8?a=1&amp;b=2"',''), ['https://example.org/a.m3u8?a=1&b=2'])

    def test_one_failed_provider_keeps_other_results_and_cache(self):
        def fetch(url):
            if 'fawanews' in url:
                return FAWA
            raise sport.SportError('offline')
        with tempfile.TemporaryDirectory() as tmp, patch.object(sport, 'request', side_effect=fetch) as request:
            rows, errors = sport.events('Voetbal', Path(tmp))
            self.assertEqual(len(rows), 1)
            self.assertEqual(errors, ['StreamsCenter'])
            sport.events('Voetbal', Path(tmp))
            self.assertEqual(request.call_count, 2)

    def test_iframe_cycle_is_bounded_and_not_played(self):
        with patch.object(sport, 'request', return_value='<iframe src="/watch"></iframe>') as request:
            with self.assertRaises(sport.SportError):
                sport.resolve(dict(url='https://example.org/watch', provider='FawaNews'))
            self.assertEqual(request.call_count, 1)

    def test_bad_stream_api_is_not_an_empty_success(self):
        with patch.object(sport, 'request', return_value='<html>closed</html>'):
            with self.assertRaises(sport.SportError):
                sport.resolve(dict(url='https://streamcenter.st/watch/example', provider='StreamsCenter'))


if __name__ == '__main__':
    unittest.main()
