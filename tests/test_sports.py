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


    def test_offline_cdn_falls_back_and_preserves_headers(self):
        import io
        from urllib.error import HTTPError
        sources = [dict(url='https://a.example/live.m3u8'), dict(url='https://b.example/live.m3u8', headers={'Referer': 'https://event.example/'})]
        response = io.BytesIO(b'#EXTM3U\n#EXTINF:5,\nsegment.ts\n')
        response.geturl = lambda: sources[1]['url']
        with patch.object(sport, 'urlopen', side_effect=[HTTPError(sources[0]['url'], 404, 'offline', {}, None), response]) as request:
            self.assertEqual(sport.playable_stream(sources), sources[1])
            self.assertEqual(request.call_args[0][0].get_header('Referer'), 'https://event.example/')

    def test_empty_playlist_and_html_do_not_start_playback(self):
        import io
        for body in (b'#EXTM3U\n#EXT-X-TARGETDURATION:5\n', b'<html>Not started</html>'):
            response = io.BytesIO(body)
            response.geturl = lambda: 'https://example.org/live.m3u8'
            with patch.object(sport, 'urlopen', return_value=response):
                with self.assertRaisesRegex(sport.SportError, 'nog niet beschikbaar'):
                    sport.playable_stream([dict(url='https://example.org/live.m3u8')])

    def test_relative_master_variant_uses_redirected_base(self):
        import io
        master = io.BytesIO(b'#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=1000\nvideo/live.m3u8\n')
        master.geturl = lambda: 'https://cdn.example/new/master.m3u8'
        media = io.BytesIO(b'#EXTM3U\n#EXTINF:5,\nsegment.ts\n')
        media.geturl = lambda: 'https://cdn.example/new/video/live.m3u8'
        source = dict(url='https://example.org/master.m3u8')
        with patch.object(sport, 'urlopen', side_effect=[master, media]) as request:
            self.assertEqual(sport.playable_stream([source]), source)
            self.assertEqual(request.call_args[0][0].full_url, media.geturl())


    def test_sports_landing_has_no_network_work(self):
        with patch.object(sport, 'events') as events:
            self.assertEqual(sport.hub_events('', Path('/tmp'), '/addon')['results'], [])
            events.assert_not_called()

    def test_hub_keeps_stream_route_and_labels_no_live_status(self):
        row = dict(title='Germany vs Netherlands --- CH 1', detail='UEFA 20:45', sport='Voetbal', url='https://example.org/event', provider='FawaNews')
        with patch.object(sport, 'events', return_value=([row], [])):
            data = sport.hub_events('Voetbal', Path('/tmp'), '/addon')
        result = data['results'][0]
        self.assertEqual(result['url'], row['url'])
        self.assertEqual(result['title'], 'Germany vs Netherlands')
        self.assertEqual(result['krispijn_type'], 'sport_event')
        self.assertNotIn('LIVE', data['status'])

    def test_quality_is_available_maximum_not_claimed_playback_resolution(self):
        import io
        master = io.BytesIO(b'#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=1000,RESOLUTION=1280x720\nlive.m3u8\n')
        master.geturl = lambda: 'https://example.org/master.m3u8'
        media = io.BytesIO(b'#EXTM3U\n#EXTINF:5,\nsegment.ts\n')
        media.geturl = lambda: 'https://example.org/live.m3u8'
        with patch.object(sport, 'urlopen', side_effect=[master, media]):
            result = sport.playable_stream([dict(url=master.geturl())])
        self.assertEqual(result['quality'], 'Bron biedt maximaal 720p')


if __name__ == '__main__':
    unittest.main()
