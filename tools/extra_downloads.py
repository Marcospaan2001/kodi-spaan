"""Originele installatiepakketten voor de bestaande Kodi-bronpagina."""
import hashlib
import io
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

PACKAGES = (
    ("repository.thecrew", "0.3.8",
     "https://team-crew.github.io/repository.thecrew-0.3.8.zip",
     "686e616ecd7d60906fd7975fe9ccaa09360c8cf0c65ba3431e6d81700b0f6ec0"),
    ("service.subtitles.opensubtitles-com", "1.0.90",
     "https://mirrors.kodi.tv/addons/omega/service.subtitles.opensubtitles-com/service.subtitles.opensubtitles-com-1.0.90.zip",
     "e327c92ac9d09bfcb2330eb217a15632b3b04d655ccf064aaf8a33e3f04c7660"),
)

def prepare_downloads(docs):
    folder = docs / "downloads"
    folder.mkdir(parents=True, exist_ok=True)
    for addon_id, version, url, expected in PACKAGES:
        target = folder / f"{addon_id}-{version}.zip"
        data = target.read_bytes() if target.exists() else None
        if data is None or hashlib.sha256(data).hexdigest() != expected:
            request = urllib.request.Request(
                url, headers={"User-Agent": "kodi-spaan-build/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read(16 * 1024 * 1024 + 1)
        if len(data) > 16 * 1024 * 1024:
            raise ValueError(f"Download te groot: {addon_id}")
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Checksum wijkt af: {addon_id}. Niet publiceren.")
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"Beschadigde zip: {addon_id}")
            addon = ET.fromstring(archive.read(f"{addon_id}/addon.xml"))
            if addon.get("id") != addon_id or addon.get("version") != version:
                raise ValueError(f"Onverwacht installatiepakket: {addon_id}")
        target.write_bytes(data)
        print(f"  extra download: {target.name}, SHA256 akkoord")
