"""Zelfstandige Kodi-interface met één cataloguswerker en directe bediening."""
import json
import os
import sqlite3
import threading
from pathlib import Path
from urllib.parse import urlencode

NAV=[('home','Filmavond'),('trending','Trending'),('cinema','Bioscoop'),('tv','Series'),('genres','Genres en filters'),('continue','Verder kijken'),('stop','Afspelen stoppen'),('settings','Instellen')]
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
            self.groups={};self.active_list=60;self.focus_results=False; self.extra={}; self.history=[]; self.artist=saved_art; self.started=False

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
            self.load(initial if initial in ('home','trending','cinema','tv','movie','search','continue','action','scifi') else 'home',query=(params or {}).get('query',''))

        def load(self,section,page=1,query='',extra=None):
            self.focus_results=self.getFocusId() in (60,61,62,70)
            if self.focus_results:self.setFocusId(50)
            self.section,self.page,self.query=section,page,query
            self.extra=extra or {}
            self.generation+=1
            self.setProperty('section',dict(NAV).get(section,{'search':'Zoeken','movie':'Films','episodes':'Afleveringen','seasons':'Seizoenen'}.get(section,'Films')))
            self.setProperty('status','Even ophalen…');self.setProperty('loading','true')
            self.setProperty('welcome','true' if section=='home' else '')
            self.setProperty('home','true' if section=='home' else '')
            self.setProperty('season_title',seasonal_selection()[0])
            self.setProperty('resume_status','Nog niets om te hervatten')
            self.setProperty('season_status','Wordt geladen…')
            for cid in (60,61,62):self.getControl(cid).reset()
            self.rows=[];self.groups={};self.active_list=61 if section=='home' else 60
            self.setProperty('title','Een avond voor ons samen' if section=='home' else dict(NAV).get(section,'Kies wat je wilt kijken'))
            self.setProperty('overview','Films en series, op jouw tempo.');self.setProperty('detail','')
            self.getControl(201).setImage('')
            self.setProperty('action','')
            with self.condition:
                self.pending=(self.generation,section,page,query,dict(self.extra));self.condition.notify()

        def worker(self):
            while True:
                with self.condition:
                    self.condition.wait_for(lambda:self.pending is not None or self.closed)
                    if self.closed:return
                    job=self.pending;self.pending=None
                gen,section,page,query,extra=job
                self.catalogue.cancelled=lambda:self.closed or gen!=self.generation
                try:
                    if section=='home':
                        try: ongoing=self.progress()['results']
                        except (sqlite3.Error,ValueError,IndexError): ongoing=[]
                        if self.closed or gen!=self.generation:continue
                        self.present({'results':ongoing},section,1,61)
                        self.setProperty('resume_status','' if ongoing else 'Je onafgekeken films en series verschijnen hier.')
                        for category,cid,status in [('home',62,'season_status')]:
                            if self.closed or gen!=self.generation:break
                            try:
                                data=self.catalogue.fetch(category)
                                if self.closed or gen!=self.generation:break
                                self.present(dict(data,results=data['results'][:12]),section,1,cid)
                                self.setProperty(status,'' if data['results'] else 'Geen titels gevonden. Bekijk het volledige overzicht.')
                            except (CatalogueError,OSError):
                                if gen==self.generation:self.setProperty(status,'Tijdelijk niet beschikbaar. Kies Opnieuw.')
                        if gen==self.generation:self.setProperty('loading','')
                        continue
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

        def present(self,data,section,page,cid=60):
            self.groups[cid]=data['results']
            if cid==60:self.rows=data['results'];self.pages=data.get('total_pages',1)
            items=[]
            for row in data['results']:
                kind=row['krispijn_type'];title=row.get('title') or row.get('name') or 'Onbekende titel'
                if kind=='episode':title=f"{row.get('episode_number','')}. {title}"
                item=xbmcgui.ListItem(label=title)
                poster=row.get('poster_path') or row.get('still_path') or ''
                poster='https://image.tmdb.org/t/p/w342'+poster if poster.startswith('/') else poster
                item.setArt({'poster':poster or 'DefaultVideo.png','thumb':poster or 'DefaultVideo.png'})
                item.setProperty('score',f"TMDb {float(row.get('vote_average') or 0):.1f}" if row.get('vote_average') else '')
                item.setProperty('group',row.get('krispijn_group',''))
                percent=max(0,min(100,float(row.get('krispijn_progress') or 0)))
                item.setProperty('progress',str(int(percent)))
                item.setProperty('has_progress','true' if percent>0 else '')
                item.setProperty('caption',f'{int(percent)}% bekeken' if percent>0 else item.getProperty('score'))
                item.setProperty('kind',{'movie':'FILM','tvshow':'SERIE','season':'SEIZOEN','episode':'AFLEVERING'}[kind])
                items.append(item)
                if kind in ('movie','tvshow') and not row.get('krispijn_route'):self.artist[f"{kind}:{row['id']}"]=row
            if cid!=60 and not items:items.append(xbmcgui.ListItem(label='Nog geen titels'))
            position=max(0,self.getControl(cid).getSelectedPosition())
            self.getControl(cid).reset()
            self.getControl(cid).addItems(items)
            if items:self.getControl(cid).selectItem(min(position,len(items)-1))
            if self.focus_results and items:
                self.focus_results=False;self.active_list=cid;self.setFocusId(cid)
            if cid!=60:
                self.focus_details();return
            self.setProperty('page',f'Pagina {page} van {self.pages}')
            self.setProperty('has_previous','true' if page>1 else '')
            self.setProperty('has_next','true' if page<self.pages else '')
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
                data.update(krispijn_progress=float(row[4]),krispijn_group='Verder kijken',id=row[1],krispijn_type=kind,title=row[8],name=row[8],overview=f'{int(float(row[4]))}% bekeken. Hervat waar je bent gebleven.',krispijn_route={'mode':'play_media','mediatype':row[0],'tmdb_id':row[1]})
                if row[0]=='episode':data['krispijn_route'].update(season=row[2],episode=row[3])
                rows.append(data)
                if len(rows)>=20:break
            return {'results':rows}

        def selected(self):
            rows=self.groups.get(self.active_list,[])
            pos=self.getControl(self.active_list).getSelectedPosition()
            return rows[pos] if 0<=pos<len(rows) else None

        def onFocus(self,control):
            if control in (60,61,62):self.active_list=control
            self.focus_details()

        def focus_details(self):
            if self.getFocusId() in (60,61,62):self.active_list=self.getFocusId()
            welcoming=self.section=='home' and self.getFocusId()==50
            self.setProperty('welcome','true' if welcoming else '')
            row=self.selected()
            if welcoming or not row:
                self.setProperty('title','Een avond voor ons samen' if self.section=='home' else 'Kies wat je wilt kijken')
                self.setProperty('overview','')
                self.setProperty('detail','')
                self.setProperty('action','')
                self.getControl(201).setImage('')
                return
            self.setProperty('action','Verder kijken' if row.get('krispijn_progress') else 'Film afspelen' if row['krispijn_type']=='movie' else 'Aflevering afspelen' if row['krispijn_type']=='episode' else 'Bekijk afleveringen' if row['krispijn_type']=='season' else 'Bekijk seizoenen')
            self.setProperty('title',row.get('title') or row.get('name',''))
            self.setProperty('overview',row.get('overview') or 'Kies deze titel om verder te gaan.')
            year=(row.get('release_date') or row.get('first_air_date') or row.get('air_date') or '')[:4]
            score=f"TMDb {float(row.get('vote_average') or 0):.1f}" if row.get('vote_average') else ''
            self.setProperty('detail','  •  '.join(x for x in [row.get('krispijn_group',''),f"{int(row['krispijn_progress'])}% bekeken" if row.get('krispijn_progress') else '',year,score] if x))
            self.getControl(201).setImage(self.getControl(self.active_list).getSelectedItem().getArt('poster'))

        def onAction(self,action):
            if action.getId() in (9,10,92,216,247):
                if self.history:
                    section,page,query,extra=self.history.pop();self.load(section,page,query,extra)
                elif self.getFocusId()!=50:self.setFocusId(50)
                else:self.close()
            elif action.getId() in (1,2,3,4,7,107):self.focus_details()

        def onClick(self,control):
            if control==80:
                query=xbmcgui.Dialog().input('Zoek films en series',defaultt=self.query).strip()
                if len(query)>=2:self.history=[];self.load('search',query=query);self.setFocusId(60)
                return
            if control==74:self.show_trailer();return
            if control==75:
                row=self.selected()
                if row:xbmcgui.Dialog().textviewer(row.get('title') or row.get('name','Beschrijving'),row.get('overview') or 'Geen beschrijving beschikbaar.')
                return
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
            elif control in (60,61,62,70):
                if control in (60,61,62):self.active_list=control
                row=self.selected()
                if not row:return
                play=route(row)
                if play:
                    xbmc.executebuiltin('PlayMedia('+BASE+urlencode(play)+')')
                else:
                    self.history.append((self.section,self.page,self.query,dict(self.extra)))
                    if row['krispijn_type']=='tvshow':self.load('seasons',extra={'tmdb_id':row['id']})
                    else:self.load('episodes',extra={'tmdb_id':row['krispijn_show_id'],'season':row['season_number']})
            elif control==71 and self.page>1:self.load(self.section,self.page-1,self.query,self.extra)
            elif control==72 and self.page<self.pages:self.load(self.section,self.page+1,self.query,self.extra)
            elif control in (73,82):self.load(self.section,self.page,self.query,self.extra)

        def show_trailer(self):
            row=self.selected()
            if not row:return
            if not xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
                if xbmcgui.Dialog().yesno('Trailers','Voor trailers is de YouTube-add-on nodig. Nu installeren?'):
                    xbmc.executebuiltin('InstallAddon(plugin.video.youtube)')
                return
            if xbmc.Player().isPlayingVideo():
                if not xbmcgui.Dialog().yesno('Trailer bekijken','De huidige video wordt gestopt. Trailer starten?'):return
                xbmc.Player().stop()
            progress=xbmcgui.DialogProgress()
            progress.create('Trailer','Trailer ophalen…')
            result={}
            def lookup():
                try:result['video']=self.catalogue.trailer(row)
                except (CatalogueError,OSError):result['error']=True
            task=threading.Thread(target=lookup,daemon=True);task.start()
            monitor=xbmc.Monitor()
            while task.is_alive():
                if progress.iscanceled() or monitor.waitForAbort(.1):progress.close();return
            progress.close()
            if result.get('error'):
                xbmcgui.Dialog().ok('Trailer','De trailerinformatie is tijdelijk niet beschikbaar.');return
            video=result.get('video')
            if not video:
                xbmcgui.Dialog().ok('Trailer','Voor deze titel is geen trailer beschikbaar.');return
            filename='Krispijn-Trailer-Fuse.xml' if xbmc.getSkinDir().startswith('skin.arctic.fuse.') else 'Krispijn-Trailer.xml'
            preview=Trailer(filename,addon.getAddonInfo('path'),'Default','1080i',video=video)
            preview.doModal()
            del preview

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

    class Trailer(xbmcgui.WindowXMLDialog):
        def __init__(self,*args,**kwargs):
            self.video=kwargs.pop('video');self.started=False
            super().__init__(*args,**kwargs)
        def onInit(self):
            if self.started:return
            self.started=True
            self.setProperty('title',self.video.get('name','Trailer'))
            self.setFocusId(91)
            url='plugin://plugin.video.youtube/play/?'+urlencode({'video_id':self.video['key']})
            xbmc.Player().play(url,windowed=True)
        def onClick(self,control):
            if control==91:
                if xbmc.Player().isPlayingVideo():xbmc.executebuiltin('PlayerControl(Play)')
            elif control==92:self.close()
        def onAction(self,action):
            if action.getId() in (9,10,92,216,247):self.close()
        def close(self):
            xbmc.Player().stop()
            super().close()

    try:
        migrate(addon)
        filename='Krispijn-Fuse.xml' if xbmc.getSkinDir().startswith('skin.arctic.fuse.') else 'Krispijn.xml'
        window=Cinema(filename,addon.getAddonInfo('path'),'Default','1080i')
        window.doModal();window.closed=True
        with window.condition:window.condition.notify()
        del window
    finally:marker.clearProperty('Krispijn.WindowOpen')
