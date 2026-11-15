"""Zelfstandige Kodi-interface met één cataloguswerker en directe bediening."""
import json
import os
import sqlite3
import threading
from pathlib import Path
from urllib.parse import urlencode

NAV=[('home','Filmavond'),('stop','Afspelen stoppen'),('trending','Trending'),('cinema','Nu in de bioscoop'),('movie','Films'),('tv','Series'),('action','Actie'),('scifi','Sciencefiction'),('genres','Genres en filters'),('search','Zoeken'),('continue','Verder kijken'),('settings','Instellen')]
BASE='plugin://plugin.video.krispijn/?'


def route(row):
    if row.get('krispijn_route'): return row['krispijn_route']
    kind=row['krispijn_type']
    if kind=='movie':return {'mode':'play_media','mediatype':'movie','tmdb_id':row['id']}
    if kind=='episode':return {'mode':'play_media','mediatype':'episode','tmdb_id':row['krispijn_show_id'],'season':row.get('season_number',row.get('krispijn_season')),'episode':row['episode_number']}
    return None


def launch(params=None):
    import xbmc,xbmcgui,xbmcaddon,xbmcvfs
    from modules.krispijn_catalogue import from_kodi, CatalogueError, seasonal_selection
    from modules.krispijn_accounts import offline_status,manage
    from modules.krispijn_playback_setup import migrate
    addon=xbmcaddon.Addon('plugin.video.krispijn')
    marker=xbmcgui.Window(10000)
    if marker.getProperty('Krispijn.WindowOpen')=='true': return
    marker.setProperty('Krispijn.WindowOpen','true')
    profile=Path(xbmcvfs.translatePath(addon.getAddonInfo('profile')))
    artfile=profile/'catalogue-art.json'
    try: saved_art=json.loads(artfile.read_text(encoding='utf-8'))
    except (ValueError,OSError): saved_art={}

    class Cinema(xbmcgui.WindowXML):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.catalogue=from_kodi(); self.closed=False; self.generation=0
            self.condition=threading.Condition(); self.pending=None
            self.rows=[]; self.section='home'; self.query=''; self.page=1; self.pages=1
            self.extra={}; self.history=[]; self.artist=saved_art; self.started=False

        def onInit(self):
            if self.started:return
            self.started=True
            nav=self.getControl(50)
            for key,title in NAV: nav.addItem(xbmcgui.ListItem(label=title))
            for i in range(7):self.getControl(300+i).setImage(os.path.join(addon.getAddonInfo('path'),'extras/portraits',f'portret-{i+1}.jpg'))
            self.setProperty('account',offline_status(addon));self.setProperty('welcome','true')
            self.setFocusId(50)
            threading.Thread(target=self.worker,daemon=True).start()
            initial=(params or {}).get('section','home')
            self.load(initial if initial in dict(NAV) and initial not in ('stop','settings','genres') else 'home',query=(params or {}).get('query',''))

        def load(self,section,page=1,query='',extra=None):
            self.section,self.page,self.query=section,page,query
            self.extra=extra or {}
            self.generation+=1
            self.setProperty('section',dict(NAV).get(section,'Afleveringen' if section=='episodes' else 'Seizoenen'))
            self.setProperty('status','Even ophalen…');self.setProperty('loading','true')
            self.setProperty('welcome','true' if section=='home' else '')
            self.getControl(60).reset();self.rows=[]
            self.setProperty('title','Een avond voor ons samen' if section=='home' else dict(NAV).get(section,'Kies wat je wilt kijken'))
            self.setProperty('overview','Films en series, op jouw tempo.');self.setProperty('detail','')
            self.getControl(201).setImage('')
            with self.condition:
                self.pending=(self.generation,section,page,query,dict(self.extra));self.condition.notify()

        def worker(self):
            while True:
                with self.condition:
                    self.condition.wait_for(lambda:self.pending is not None or self.closed)
                    if self.closed:return
                    job=self.pending;self.pending=None
                gen,section,page,query,extra=job
                try:
                    if section=='home':
                        try: ongoing=self.progress()['results']
                        except (sqlite3.Error,ValueError,IndexError): ongoing=[]
                        if self.closed or gen!=self.generation:continue
                        self.present({'results':ongoing,'home_label':'Verder kijken · Seizoenskeuze wordt geladen'},section,page)
                        try: data=self.catalogue.fetch('home',page=page)
                        except (CatalogueError,OSError):
                            data={'results':[], 'stale':True}
                        keys={(r['krispijn_type'],str(r['id'])) for r in ongoing}
                        picks=[dict(r,krispijn_group=seasonal_selection()[0]) for r in data['results']
                               if (r['krispijn_type'],str(r['id'])) not in keys][:12]
                        data=dict(data,results=ongoing+picks,total_pages=1,
                                  home_label=('Verder kijken · ' if ongoing else '')+seasonal_selection()[0])
                    elif section=='continue':data=self.progress()
                    else:
                        if section=='action':extra.update(media='movie',genres='28')
                        if section=='scifi':extra.update(media='movie',genres='878')
                        data=self.catalogue.fetch(section if section not in ('action','scifi') else 'movie',page=page,query=query,**extra)
                    if self.closed or gen!=self.generation:continue
                    self.present(data,section,page)
                except Exception as error:
                    if self.closed or gen!=self.generation:continue
                    self.setProperty('loading','')
                    self.setProperty('status',str(error) if isinstance(error,CatalogueError) else 'Dit overzicht kon niet laden. Kies Opnieuw.')
                    xbmc.log('Krispijn catalogus: '+type(error).__name__,xbmc.LOGERROR)

        def present(self,data,section,page):
            self.rows=data['results'];self.pages=data.get('total_pages',1)
            items=[]
            for row in self.rows:
                kind=row['krispijn_type'];title=row.get('title') or row.get('name') or 'Onbekende titel'
                if kind=='episode':title=f"{row.get('episode_number','')}. {title}"
                item=xbmcgui.ListItem(label=title)
                poster=row.get('poster_path') or row.get('still_path') or ''
                poster='https://image.tmdb.org/t/p/w342'+poster if poster.startswith('/') else poster
                item.setArt({'poster':poster or 'DefaultVideo.png','thumb':poster or 'DefaultVideo.png'})
                item.setProperty('score',f"TMDb {float(row.get('vote_average') or 0):.1f}" if row.get('vote_average') else '')
                item.setProperty('group',row.get('krispijn_group',''))
                item.setProperty('kind',{'movie':'FILM','tvshow':'SERIE','season':'SEIZOEN','episode':'AFLEVERING'}[kind])
                items.append(item)
                if kind in ('movie','tvshow') and not row.get('krispijn_route'):self.artist[f"{kind}:{row['id']}"]=row
            position=max(0,self.getControl(60).getSelectedPosition())
            self.getControl(60).reset()
            self.getControl(60).addItems(items)
            if items:self.getControl(60).selectItem(min(position,len(items)-1))
            self.setProperty('page',f'Pagina {page} van {self.pages}')
            self.setProperty('status',('Bewaarde resultaten: geen verbinding' if data.get('stale') else f'{len(items)} titels') if items else ('Hier staan straks je onafgekeken films en afleveringen.' if section=='continue' else 'Geen resultaten. Probeer een andere zoekterm of categorie.'))
            self.setProperty('loading','')
            if data.get('home_label'):self.setProperty('status',data['home_label']+(' · Seizoenskeuze niet bereikbaar' if data.get('stale') else ''))
            self.focus_details()

        def progress(self):
            file=profile/'watched.db'
            if not file.exists():return {'results':[]}
            conn=sqlite3.connect('file:'+str(file)+'?mode=ro',uri=True,timeout=1)
            try: records=conn.execute('SELECT * FROM progress ORDER BY last_played DESC LIMIT 100').fetchall()
            finally:conn.close()
            rows=[];seen=set()
            for row in records:
                if row[0] not in ('movie','episode') or not 0<float(row[4])<95:continue
                kind='movie' if row[0]=='movie' else 'tvshow';key=f'{kind}:{row[1]}'
                if key in seen:continue
                seen.add(key);data=dict(self.artist.get(key,{}))
                data.update(krispijn_group='Verder kijken',id=row[1],krispijn_type=kind,title=row[8],name=row[8],overview=f'{int(float(row[4]))}% bekeken. Hervat waar je bent gebleven.',krispijn_route={'mode':'play_media','mediatype':row[0],'tmdb_id':row[1]})
                if row[0]=='episode':data['krispijn_route'].update(season=row[2],episode=row[3])
                rows.append(data)
                if len(rows)>=20:break
            return {'results':rows}

        def focus_details(self):
            welcoming = self.section == 'home' and self.getFocusId() != 60
            self.setProperty('welcome', 'true' if welcoming else '')
            if welcoming:
                self.setProperty('title', 'Een avond voor ons samen')
                self.setProperty('overview', 'Welkom bij Familie Krispijn. Kies een film of serie en maak het gezellig.')
                self.setProperty('detail', 'ONZE EIGEN BIOSCOOP')
                self.getControl(201).setImage('')
                return
            if not self.rows:return
            pos=self.getControl(60).getSelectedPosition()
            if not 0<=pos<len(self.rows):return
            row=self.rows[pos]
            self.setProperty('title',row.get('title') or row.get('name',''))
            self.setProperty('overview',row.get('overview') or 'Kies deze titel om verder te gaan.')
            year=(row.get('release_date') or row.get('first_air_date') or row.get('air_date') or '')[:4]
            score=f"TMDb {float(row.get('vote_average') or 0):.1f}" if row.get('vote_average') else ''
            self.setProperty('detail','  •  '.join(x for x in [row.get('krispijn_group',''),year,score] if x))
            self.getControl(201).setImage(self.getControl(60).getSelectedItem().getArt('poster'))

        def onAction(self,action):
            if action.getId() in (9,10,92,216,247):
                if self.history:
                    section,page,query,extra=self.history.pop();self.load(section,page,query,extra)
                elif self.getFocusId()!=50:self.setFocusId(50)
                else:self.close()
            elif action.getId() in (1,2,3,4,7,107):self.focus_details()

        def onClick(self,control):
            if control==50:
                section=NAV[self.getControl(50).getSelectedPosition()][0]
                if section=='stop':
                    player=xbmc.Player()
                    if player.isPlayingVideo():
                        player.stop()
                    else:
                        xbmcgui.Dialog().notification('Familie Krispijn','Er wordt geen video afgespeeld.',time=2500)
                    return
                if section=='settings':self.settings();return
                if section=='search':
                    query=xbmcgui.Dialog().input('Zoek films en series',defaultt=self.query).strip()
                    if len(query)<2:return
                    self.history=[];self.load('search',query=query);return
                if section=='genres':self.filters();return
                self.history=[];self.load(section)
            elif control==60 and self.rows:
                pos=self.getControl(60).getSelectedPosition()
                if not 0<=pos<len(self.rows):return
                row=self.rows[pos];play=route(row)
                if play:
                    xbmc.executebuiltin('PlayMedia('+BASE+urlencode(play)+')')
                else:
                    self.history.append((self.section,self.page,self.query,dict(self.extra)))
                    if row['krispijn_type']=='tvshow':self.load('seasons',extra={'tmdb_id':row['id']})
                    else:self.load('episodes',extra={'tmdb_id':row['krispijn_show_id'],'season':row['season_number']})
            elif control==71 and self.page>1:self.load(self.section,self.page-1,self.query,self.extra)
            elif control==72 and self.page<self.pages:self.load(self.section,self.page+1,self.query,self.extra)
            elif control==73:self.load(self.section,self.page,self.query,self.extra)

        def filters(self):
            dialog=xbmcgui.Dialog();choice=dialog.select('Wat wil je zien?',['Films','Series'])
            if choice<0:return
            genres= [('Actie','28'),('Avontuur','12'),('Sciencefiction','878'),('Komedie','35'),('Thriller','53'),('Misdaad','80'),('Drama','18'),('Horror','27'),('Fantasy','14'),('Animatie','16'),('Familie','10751'),('Documentaire','99'),('Romantiek','10749')] if choice==0 else [('Actie en avontuur','10759'),('Sciencefiction en fantasy','10765'),('Komedie','35'),('Misdaad','80'),('Drama','18'),('Animatie','16'),('Familie','10751'),('Documentaire','99')]
            selected=dialog.multiselect('Kies genres',[g[0] for g in genres])
            if selected is None:return
            year=dialog.input('Jaar (leeg = alle jaren)',type=xbmcgui.INPUT_NUMERIC)
            rating=dialog.select('Minimale TMDb-score',['Alle scores','6 of hoger','7 of hoger','8 of hoger'])
            extra={'media':'movie' if choice==0 else 'tv','genres':','.join(genres[i][1] for i in selected)}
            if year.isdigit() and 1900<=int(year)<=2100:extra['year']=year
            if rating>0:extra['min_rating']=rating+5
            self.load('movie' if choice==0 else 'tv',extra=extra)

        def settings(self):
            dialog=xbmcgui.Dialog()
            selection=dialog.select('Instellen',[offline_status(addon),'OpenSubtitles (optioneel)','Uitgebreide instellingen','Over Familie Krispijn'])
            if selection==0:manage();self.setProperty('account',offline_status(addon))
            elif selection==1:
                sid='service.subtitles.opensubtitles-com'
                if xbmc.getCondVisibility('System.HasAddon('+sid+')'):xbmcaddon.Addon(sid).openSettings()
                else:xbmc.executebuiltin('InstallAddon('+sid+')')
            elif selection==2:addon.openSettings()
            elif selection==3:dialog.ok('Familie Krispijn','Een avond voor ons samen.[CR]Versie '+addon.getAddonInfo('version')+'[CR]TMDb levert de catalogus en scores.[CR]Gebaseerd op POV van kodifitzwell, GPL-3.0. Skin: Arctic Fuse van jurialmunkey, CC BY-NC-SA 4.0.')

        def close(self):
            self.closed=True
            with self.condition:self.condition.notify()
            try:
                profile.mkdir(parents=True,exist_ok=True)
                artfile.write_text(json.dumps(dict(list(self.artist.items())[-500:])),encoding='utf-8')
            except OSError:pass
            super().close()

    try:
        migrate(addon)
        filename='Krispijn-Fuse.xml' if xbmc.getSkinDir().startswith('skin.arctic.fuse.') else 'Krispijn.xml'
        window=Cinema(filename,addon.getAddonInfo('path'),'Default','1080i')
        window.doModal();window.closed=True
        with window.condition:window.condition.notify()
        del window
    finally:marker.clearProperty('Krispijn.WindowOpen')
