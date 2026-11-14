"""Zelfstandig venster zodat afspelen een vrije plugin-aanroep krijgt."""
import sys
from urllib.parse import parse_qsl

from modules.krispijn_experience import launch

params = dict(parse_qsl(sys.argv[1].lstrip('?'))) if len(sys.argv) > 1 else {}
launch(params)
