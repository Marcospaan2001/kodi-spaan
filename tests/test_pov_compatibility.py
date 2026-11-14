import ast
from pathlib import Path
import unittest
from urllib.parse import urlencode, urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / 'build/plugin.video.krispijn'


class PovCompatibility(unittest.TestCase):
    def helpers(self):
        tree = ast.parse((ADDON / 'resources/lib/modules/kodi_utils.py').read_text())
        selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('build_url', 'skin_location')]
        ns = {'urlencode': urlencode}
        exec(compile(ast.Module(body=selected, type_ignores=[]), 'pov_helpers', 'exec'), ns)
        return ns

    def test_movie_urls_target_our_addon(self):
        url = self.helpers()['build_url']({'mode': 'play_media', 'tmdb_id': '123'})
        self.assertEqual(urlparse(url).netloc, 'plugin.video.krispijn')

    def test_next_page_keeps_page_and_genre(self):
        url = self.helpers()['build_url']({'mode': 'build_movie_list', 'action': 'tmdb_movies_genres', 'genre_id': '878', 'new_page': '2'})
        self.assertEqual(urlparse(url).netloc, 'plugin.video.krispijn')
        self.assertEqual(parse_qs(urlparse(url).query)['new_page'], ['2'])
        self.assertEqual(parse_qs(urlparse(url).query)['genre_id'], ['878'])

    def test_auth_window_uses_existing_fork_files(self):
        location = self.helpers()['skin_location']()
        self.assertEqual(location, 'special://home/addons/plugin.video.krispijn')
        self.assertTrue((ADDON / 'resources/skins/Default/1080i/progress_media.xml').is_file())

    def test_kodi21_video_info_tag_takes_no_arguments(self):
        calls = []
        for path in (ADDON / 'resources/lib').rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8-sig'))
            for n in ast.walk(tree):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'getVideoInfoTag':
                    calls.append(n)
                    self.assertFalse(n.args or n.keywords, str(path))
        self.assertGreaterEqual(len(calls), 3)


if __name__ == '__main__':
    unittest.main()
