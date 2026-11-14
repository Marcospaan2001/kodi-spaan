"""Gerichte Kodi 21-optimalisaties; Kodi 22 blijft ongewijzigd."""
import json


def patch_fast(p):
    startup = 'shortcuts/skinvariables-startup.json'
    path = p.skin_dir / startup
    original = path.read_bytes().decode('utf-8')
    data = json.loads(original)
    actions = data['actions'][0][0]['value']
    previous = [i for i, value in enumerate(actions)
                if isinstance(value, dict) and value.get('rules') == ['!Skin.HasSetting(Krispijn.PerformanceV1)']]
    if len(previous) != 1:
        raise ValueError('Verwachte vorige prestatiemigratie ontbreekt')
    actions.insert(previous[0] + 1, {
        'rules': ['!Skin.HasSetting(Krispijn.PerformanceV2)'],
        'value': [
            'Skin.Reset(TMDbHelper.EnableBlur)',
            'Skin.SetString(Background.ArtworkStyle,Simple)',
            'Skin.Reset(Background.DialogImage)',
            'Skin.Reset(TMDbHelper.Service)',
            'Skin.SetString(CustomRating.Movies.Item01,TMDb)',
            'Skin.SetString(CustomRating.TVShows.Item01,TMDb)',
            'Skin.SetBool(Krispijn.FastMode)',
            'Skin.SetBool(Krispijn.PerformanceV2)',
        ],
    })
    native = ('Skin.HasSetting(Krispijn.FastMode) + !Skin.HasSetting(DisableMonochromeHighlight) + '
              'String.IsEmpty(Skin.String(SkinVariables.SkinUser))')
    generated = '![' + native + ']'
    for command in (
        'SetProperty(InitStatus,Generating Textures)',
        'Skin.Reset(TextureMaker.Built)',
        'route=run_executebuiltin=special://skin/shortcuts/skinvariables-build-colortemplates.json&use_rules=True&get_values=true',
    ):
        if actions.count(command) != 1:
            raise ValueError('Onverwachte textuurgeneratie in startup')
        actions[actions.index(command)] = {'rules': [generated], 'value': command}
    actions.insert(previous[0] + 2, {'rules': [native], 'value': 'Skin.SetBool(TextureMaker.Built)'})
    p.replace(startup, original, json.dumps(data, indent=4, ensure_ascii=False) + '\n')
    # De portretten blijven bereikbaar wanneer ze vanuit een andere skin zijn gekozen.
    p.replace('1080i/Includes_Krispijn.xml', '<variable name="Krispijn_FacesPath">',
              '<variable name="Krispijn_FacesPath">\n'
              '        <value condition="System.HasAddon(plugin.video.krispijn) + !String.IsEmpty(Addon.SettingStr(plugin.video.krispijn,krispijn.family.path))">'
              '$INFO[Addon.SettingStr(plugin.video.krispijn,krispijn.family.path)]</value>')
    # Privébeelden staan op het apparaat. Geen terugval op de smileys.
    p.replace('1080i/Includes_Krispijn.xml',
              '<value>special://skin/extras/krispijn/faces/</value>',
              '<value>special://profile/addon_data/skin.arctic.fuse.2.krispijn/faces/</value>')
    p.replace('1080i/Includes_Krispijn.xml',
              '<control type="group">\n            <centerleft>50%</centerleft>',
              '<control type="group" id="99871">\n            <centerleft>50%</centerleft>')
    p.replace('1080i/Includes_Krispijn.xml',
              '<control type="group">\n            <visible>!Skin.HasSetting(Krispijn.DisableFaces)</visible>',
              '<control type="group" id="99872">\n            <visible>!Skin.HasSetting(Krispijn.DisableFaces)</visible>')
    for group, token in (
        ('99871', 'time="500" tween="sine" easing="inout" pulse="true" condition="true"'),
        ('99872', 'time="900" tween="sine" easing="inout" pulse="true" condition="true"'),
        ('99872', 'time="1400" tween="sine" easing="inout" pulse="true" condition="true"'),
    ):
        p.replace('1080i/Includes_Krispijn.xml', token,
                  token.replace('condition="true"', f'condition="Control.IsVisible({group})"'))
    p.replace('1080i/Includes_Krispijn.xml', '<timeperimage>1800</timeperimage>',
              '<timeperimage>5000</timeperimage>')
