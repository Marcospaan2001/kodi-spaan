"""Eigen zichtbare namen; modulepaden en licenties blijven behouden."""
import io
import re
import shutil
import tokenize
import xml.etree.ElementTree as ET


def apply_branding(folder):
    for path in (folder / 'resources').rglob('*.py'):
        text = path.read_text(encoding='utf-8-sig')
        tokens = []
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.STRING:
                # Lowercase pov IDs, provider keys and URLs are not branding.
                token = token._replace(string=re.sub(r'\bPOV\b', 'Krispijn', token.string))
            tokens.append(token)
        path.write_bytes(tokenize.untokenize(tokens).encode('utf-8'))
    for path in (folder / 'resources').rglob('*.xml'):
        tree = ET.parse(path)
        for node in tree.iter():
            if node.text:
                node.text = re.sub(r'\bPOV\b', 'Krispijn', node.text)
            for key in ('label', 'values', 'default'):
                if node.get(key):
                    node.set(key, re.sub(r'\bPOV\b', 'Krispijn', node.get(key)))
        path.write_bytes(ET.tostring(tree.getroot(), encoding='utf-8', xml_declaration=True))
    for path in (folder / 'resources').rglob('*.po'):
        path.write_bytes(re.sub(r'\bPOV\b', 'Krispijn', path.read_text(encoding='utf-8-sig')).encode('utf-8'))
    # Compatibility image aliases referenced by old dialogs also use our art.
    for old, new in [('pov.png', 'icon.png'), ('pov_poster.png', 'icon.png')]:
        shutil.copyfile(folder / new, folder / old)
    (folder / 'pov_fanart.png').unlink(missing_ok=True)
