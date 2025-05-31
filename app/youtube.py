import os
import yt_dlp

class YouTubeDownloader:
    def __init__(self):
        # Percorso relativo per i cookie, funzionerà dalla directory principale del progetto
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.cookie_path = os.path.join(self.base_dir, 'cookies.txt')
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'ignoreerrors': True,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'cookiefile': self.cookie_path,
        }

    def analyze_url(self, url):
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_info = {
                    'title': info.get('title', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', ''),
                    'video_formats': [],
                    'audio_formats': [],
                    'subtitle_languages': []
                }
                
                print("\n=== ANALISI FORMATI COMPLETA ===")
                print(f"URL: {url}")
                print(f"Totale formati disponibili: {len(info.get('formats', []))}")
                
                # Lista completa degli ID formati audio noti di YouTube
                known_audio_formats = {
                    '140': 'm4a (aac) - 128k',
                    '139': 'm4a (aac) - 48k', 
                    '251': 'webm (opus) - ~160k',
                    '250': 'webm (opus) - ~70k',
                    '249': 'webm (opus) - ~50k',
                    '599': 'm4a (aac) - ultralow',
                    '600': 'webm (opus) - ultralow'
                }
                
                # Estensioni e codec audio validi
                audio_extensions = ['m4a', 'webm', 'opus', 'mp3', 'aac', 'ogg', 'flac', 'wav']
                audio_codecs = ['opus', 'aac', 'mp4a', 'mp3', 'vorbis', 'flac', 'alac']
                
                print(f"\nFormati audio noti YouTube: {list(known_audio_formats.keys())}")
                print(f"Estensioni audio supportate: {audio_extensions}")
                print(f"Codec audio supportati: {audio_codecs}")
                
                # Raccogli tutti i formati disponibili
                for i, f in enumerate(info.get('formats', [])):
                    format_data = {
                        'format_id': f.get('format_id', ''),
                        'ext': f.get('ext', ''),
                        'filesize': f.get('filesize', 0),
                        'format_note': f.get('format_note', ''),
                    }
                    
                    vcodec = f.get('vcodec', 'none')
                    acodec = f.get('acodec', 'none')
                    ext = f.get('ext', '')
                    format_id = str(f.get('format_id', ''))
                    format_note = str(f.get('format_note', '')).lower()
                    abr = f.get('abr', 0)
                    tbr = f.get('tbr', 0)
                    
                    print(f"\n--- Formato {i+1}/{len(info.get('formats', []))} ---")
                    print(f"ID: {format_id}")
                    print(f"Estensione: {ext}")
                    print(f"Video codec: {vcodec}")
                    print(f"Audio codec: {acodec}")
                    print(f"Format note: {format_note}")
                    print(f"Audio bitrate: {abr}")
                    print(f"Total bitrate: {tbr}")
                    print(f"Filesize: {f.get('filesize', 'N/A')}")
                    
                    # LOGICA MULTI-LIVELLO PER IDENTIFICARE FORMATI AUDIO
                    is_audio = False
                    detection_method = ""
                    
                    # LIVELLO 1: ID formato noto di YouTube (priorità massima)
                    if format_id in known_audio_formats:
                        is_audio = True
                        detection_method = f"ID YouTube noto ({known_audio_formats[format_id]})"
                    
                    # LIVELLO 2: Logica classica vcodec='none' + acodec valido
                    elif (str(vcodec).lower() == 'none' and 
                          str(acodec).lower() not in ['none', 'null', ''] and 
                          acodec is not None):
                        is_audio = True
                        detection_method = "vcodec=none + acodec valido"
                    
                    # LIVELLO 3: Estensione audio + nessun video codec
                    elif (ext.lower() in audio_extensions and 
                          str(vcodec).lower() in ['none', 'null', '']):
                        is_audio = True
                        detection_method = "estensione audio + no vcodec"
                    
                    # LIVELLO 4: Codec audio riconosciuto
                    elif any(codec in str(acodec).lower() for codec in audio_codecs):
                        # Verifica che non sia un formato video con audio
                        if str(vcodec).lower() in ['none', 'null', ''] or vcodec is None:
                            is_audio = True
                            detection_method = "codec audio riconosciuto"
                    
                    # LIVELLO 5: Format note contiene 'audio'
                    elif ('audio' in format_note and 
                          'video' not in format_note and 
                          'visual' not in format_note):
                        is_audio = True
                        detection_method = "format_note contiene 'audio'"
                    
                    # LIVELLO 6: Estensione audio senza codec video definito
                    elif (ext.lower() in audio_extensions and 
                          (vcodec is None or str(vcodec).strip() == '')):
                        is_audio = True
                        detection_method = "estensione audio + vcodec indefinito"
                    
                    # LIVELLO 7: Fallback per formati sospetti
                    elif (ext.lower() in ['m4a', 'webm'] and 
                          abr > 0 and 
                          str(vcodec).lower() != 'vp9'):
                        is_audio = True
                        detection_method = "fallback m4a/webm con bitrate"
                    
                    print(f"Rilevamento audio: {is_audio}")
                    if is_audio:
                        print(f"Metodo: {detection_method}")
                    
                    if is_audio:
                        # Aggiungi informazioni specifiche per l'audio
                        if abr:
                            format_data['bitrate'] = abr
                        elif tbr:
                            format_data['bitrate'] = tbr
                        
                        # Migliora la descrizione del formato
                        if not format_data['format_note']:
                            if format_id in known_audio_formats:
                                format_data['format_note'] = known_audio_formats[format_id]
                            else:
                                format_data['format_note'] = f"{ext.upper()} Audio"
                        
                        video_info['audio_formats'].append(format_data)
                        print(f"✅ AGGIUNTO COME AUDIO")
                    
                    # Identifica i formati VIDEO
                    elif (vcodec and 
                          str(vcodec).lower() not in ['none', 'null', ''] and 
                          vcodec is not None):
                        format_data['resolution'] = f.get('resolution', '') or f.get('height', '')
                        if format_data['resolution'] and not str(format_data['resolution']).endswith('p'):
                            format_data['resolution'] = f"{format_data['resolution']}p"
                        video_info['video_formats'].append(format_data)
                        print(f"✅ AGGIUNTO COME VIDEO")
                    else:
                        print(f"❌ SCARTATO")
                
                print(f"\n=== RISULTATI FINALI ===")
                print(f"Formati video trovati: {len(video_info['video_formats'])}")
                print(f"Formati audio trovati: {len(video_info['audio_formats'])}")
                
                # Debug dettagliato per formati audio
                if video_info['audio_formats']:
                    print("\n🎵 FORMATI AUDIO IDENTIFICATI:")
                    for i, af in enumerate(video_info['audio_formats'], 1):
                        bitrate_info = f", {af.get('bitrate', 'N/A')}k" if af.get('bitrate') else ""
                        size_info = f", {round(af['filesize']/1024/1024, 1)}MB" if af.get('filesize') else ""
                        print(f"  {i}. ID: {af['format_id']}, {af['ext'].upper()}, {af.get('format_note', 'N/A')}{bitrate_info}{size_info}")
                else:
                    print("\n⚠️  NESSUN FORMATO AUDIO TROVATO!")
                    print("\n🔍 DIAGNOSI POSSIBILI CAUSE:")
                    print("1. Il video potrebbe non avere formati audio separati")
                    print("2. yt-dlp potrebbe aver cambiato la struttura dei dati")
                    print("3. Il video potrebbe essere protetto o non disponibile")
                    print("4. Problema di connessione o accesso a YouTube")
                    
                    # Mostra tutti i formati per debug
                    print("\n📋 TUTTI I FORMATI DISPONIBILI:")
                    for f in info.get('formats', [])[:10]:  # Mostra solo i primi 10
                        print(f"  - ID: {f.get('format_id')}, ext: {f.get('ext')}, vcodec: {f.get('vcodec')}, acodec: {f.get('acodec')}")
                
                print("=== FINE ANALISI ===\n")
                
                # Rimuovi duplicati e ordina per qualità
                video_info['video_formats'] = sorted(
                    list({f['format_id']: f for f in video_info['video_formats']}.values()),
                    key=lambda x: int(str(x.get('resolution', '0p')).replace('p', '')) if str(x.get('resolution', '')).replace('p', '').isdigit() else 0,
                    reverse=True
                )
                
                # Ordina i formati audio per bitrate se disponibile, altrimenti per filesize
                video_info['audio_formats'] = sorted(
                    list({f['format_id']: f for f in video_info['audio_formats']}.values()),
                    key=lambda x: x.get('bitrate', 0) or (x.get('filesize', 0) // 1000000) or 0,
                    reverse=True
                )
                
                # Gestione sottotitoli
                for lang, subs in info.get('subtitles', {}).items():
                    video_info['subtitle_languages'].append({
                        'language': lang,
                        'formats': [s.get('ext', '') for s in subs],
                        'automatic': False
                    })
                for lang, subs in info.get('automatic_captions', {}).items():
                    video_info['subtitle_languages'].append({
                        'language': lang,
                        'formats': [s.get('ext', '') for s in subs],
                        'automatic': True
                    })
                
                return video_info
        except Exception as e:
            print(f"Errore nell'analisi URL: {str(e)}")
            return {'error': str(e)}

    def download_video(self, url, format_id, output_dir='downloads'):
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            filename = f"{output_dir}/%(title)s.%(ext)s"
            
            # Configurazione migliorata per il download video+audio
            ydl_opts = {
                # Formato principale + miglior audio disponibile, con fallback al miglior formato complessivo
                'format': f'{format_id}+bestaudio/best',  # Semplificato per maggiore compatibilità
                'merge_output_format': 'mp4',  # Formato di output preferito dopo il merge
                'outtmpl': filename,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'ignoreerrors': False,  # Cambiato a False per vedere gli errori
                'no_warnings': False,   # Cambiato a False per vedere gli avvisi
                'quiet': False,         # Cambiato a False per vedere l'output
                'verbose': True,        # Aggiunto per debug dettagliato
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'cookiefile': self.cookie_path,
                'postprocessors': [
                    # Assicura che l'audio sia sempre incluso
                    {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
                ],
            }
            
            print(f"\n🎬 DOWNLOAD VIDEO: {url}")
            print(f"Format ID: {format_id}")
            print(f"Cookie file: {self.cookie_path} (esiste: {os.path.exists(self.cookie_path)})")
            print(f"Output directory: {output_dir} (esiste: {os.path.exists(output_dir)})")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                print(f"✅ Download completato: {downloaded_file}")
                print(f"Il file esiste: {os.path.exists(downloaded_file)}")
                return downloaded_file
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Errore nel download video: {error_msg}")
            return {'error': error_msg}

    def download_audio(self, url, format_id, output_dir='downloads'):
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            filename = f"{output_dir}/%(title)s_audio.%(ext)s"
            
            ydl_opts = {
                'format': format_id,
                'outtmpl': filename,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'ignoreerrors': True,
                'no_warnings': False,  # Cambiato per debug
                'quiet': False,        # Cambiato per debug
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'cookiefile': self.cookie_path,
            }
            
            print(f"\n🎵 DOWNLOAD AUDIO: {url}")
            print(f"Format ID: {format_id}")
            print(f"Cookie file: {self.cookie_path} (esiste: {os.path.exists(self.cookie_path)})")
            print(f"Output directory: {output_dir} (esiste: {os.path.exists(output_dir)})")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                print(f"✅ Download completato: {downloaded_file}")
                print(f"Il file esiste: {os.path.exists(downloaded_file)}")
                return downloaded_file
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Errore nel download audio: {error_msg}")
            return {'error': error_msg}

    def download_subtitle(self, url, language, subtitle_format='srt', output_dir='downloads'):
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            filename = f"{output_dir}/%(title)s_{language}.{subtitle_format}"
            
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'subtitleslangs': [language],
                'subtitlesformat': subtitle_format,
                'outtmpl': filename,
                'nocheckcertificate': True,
                'geo_bypass': True,
                'ignoreerrors': True,
                'no_warnings': False,  # Cambiato per debug
                'quiet': False,        # Cambiato per debug
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'cookiefile': self.cookie_path,
            }
            
            print(f"\n📄 DOWNLOAD SOTTOTITOLI: {url}")
            print(f"Lingua: {language}")
            print(f"Formato: {subtitle_format}")
            print(f"Cookie file: {self.cookie_path} (esiste: {os.path.exists(self.cookie_path)})")
            print(f"Output directory: {output_dir} (esiste: {os.path.exists(output_dir)})")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                base_filename = ydl.prepare_filename(info)
                subtitle_file = f"{os.path.splitext(base_filename)[0]}.{language}.{subtitle_format}"
                
                if not os.path.exists(subtitle_file):
                    error_msg = f'Sottotitoli non disponibili per la lingua {language}'
                    print(f"❌ {error_msg}")
                    return {'error': error_msg}
                    
                print(f"✅ Download completato: {subtitle_file}")
                print(f"Il file esiste: {os.path.exists(subtitle_file)}")
                return subtitle_file
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Errore nel download sottotitoli: {error_msg}")
            return {'error': error_msg}