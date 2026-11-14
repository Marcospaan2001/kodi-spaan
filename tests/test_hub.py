import ast
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import types
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hub', ROOT / 'video-mod/hub.py')
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


class HubTests(unittest.TestCase):
    def test_cinema_uses_dutch_region_and_preserves_next_page(self):
        cache = Mock(return_value={'results': [{'id': 42}], 'total_pages': 3})
        modules = {
            'xbmc': types.ModuleType('xbmc'), 'xbmcgui': types.ModuleType('xbmcgui'),
            'modules': types.ModuleType('modules'), 'modules.cache': types.SimpleNamespace(check_databases=lambda: None),
            'indexers': types.SimpleNamespace(tmdb_api=types.SimpleNamespace(get_tmdb=lambda url: None)),
            'caches': types.ModuleType('caches'), 'caches.main_cache': types.SimpleNamespace(cache_object=cache),
        }
        with patch.dict('sys.modules', modules), patch.object(hub, 'listing') as listing:
            hub.run({'mode': 'krispijn.cinema', 'page': '2'})
        self.assertIn('region=NL&page=2', cache.call_args.args[2])
        self.assertEqual(listing.call_args.kwargs['next_route'], {'mode': 'krispijn.cinema', 'page': 3})

    def test_trending_combines_types_and_only_loads_on_request(self):
        api = types.SimpleNamespace(
            tmdb_movies_trending=Mock(return_value={'results': [{'id': 1}], 'total_pages': 2}),
            tmdb_tv_trending=Mock(return_value={'results': [{'id': 1}], 'total_pages': 3}),
        )
        modules = {
            'xbmc': types.ModuleType('xbmc'), 'xbmcgui': types.ModuleType('xbmcgui'),
            'modules': types.ModuleType('modules'), 'modules.cache': types.SimpleNamespace(check_databases=lambda: None),
            'indexers': types.SimpleNamespace(tmdb_api=api),
        }
        with patch.dict('sys.modules', modules), patch.object(hub, 'listing') as listing:
            hub.run({'mode': 'krispijn.trending', 'page': '2'})
        api.tmdb_movies_trending.assert_called_once_with(2)
        api.tmdb_tv_trending.assert_called_once_with(2)
        self.assertEqual(len(listing.call_args.args[0]), 2)
        self.assertFalse(listing.call_args.kwargs['search'])
        self.assertEqual(listing.call_args.kwargs['next_route']['page'], 3)

    def test_same_tmdb_id_does_not_merge_movie_and_show(self):
        rows = hub.mixed([{'id': 1, 'title': 'Film'}], [{'id': 1, 'name': 'Serie'}])
        self.assertEqual([r['krispijn_type'] for r in rows], ['movie', 'tvshow'])

    def test_suggestions_are_bounded_and_remove_duplicates_and_adult(self):
        rows = hub.mixed([{'id': 1}, {'id': 1}, {'id': 2, 'adult': True}] + [{'id': i} for i in range(3, 30)], [])
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({r['id'] for r in rows}), 8)
        self.assertNotIn(2, [r['id'] for r in rows])

    def test_continue_combines_movies_and_exact_latest_episode(self):
        rows = [
            ('episode', 1, 1, 1, 30, 600, '2026-01-01', 0, 'Serie'),
            ('movie', 1, '', '', 50, 2000, '2026-01-02', 0, 'Film'),
            ('episode', 1, 1, 2, 25, 300, '2026-01-03', 0, 'Serie'),
            ('movie', 2, '', '', 100, 6000, '2026-01-04', 0, 'Afgekeken'),
        ]
        result = hub.progress_rows(rows)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][3], 2)
        self.assertEqual(result[1][0], 'movie')

    def test_no_progress_is_valid_empty_state(self):
        self.assertEqual(hub.progress_rows([]), [])
        self.assertEqual(hub.progress_rows([None, (), ('movie', 1)]), [])

    def test_movie_plays_but_series_opens_seasons(self):
        self.assertEqual(hub.media_route({'id': 7, 'krispijn_type': 'movie'})['mode'], 'play_media')
        self.assertEqual(hub.media_route({'id': 7, 'krispijn_type': 'tvshow'})['mode'], 'build_season_list')

    def test_skin_has_three_bounded_provider_rows_and_no_duplicate_ids(self):
        root = ET.fromstring(hub.window_xml())
        ids = [n.get('id') for n in root.findall('.//control') if n.get('id')]
        self.assertEqual(len(ids), len(set(ids)))
        contents = root.findall('.//content')
        self.assertEqual(len(contents), 3)
        self.assertTrue(all(n.get('limit') == '8' for n in contents))
        self.assertTrue(all('KrispijnHubRefresh' in n.text for n in contents))
        self.assertIn('watchedprogress', hub.window_xml())

    def test_no_keyboard_polling_or_periodic_network_service(self):
        tree = ast.parse((ROOT / 'video-mod/hub.py').read_text())
        self.assertFalse(any(isinstance(n, (ast.While, ast.AsyncFor)) for n in ast.walk(tree)))
        self.assertNotIn('Thread(', (ROOT / 'video-mod/hub.py').read_text())


if __name__ == '__main__':
    unittest.main()
