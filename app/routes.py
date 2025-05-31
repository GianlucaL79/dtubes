# routes.py
import os
from flask import Flask, render_template, request, jsonify, send_file, abort
from urllib.parse import unquote
from app import app # Importa l'istanza di app
from app.youtube import YouTubeDownloader
import time
import threading

# Usa un percorso relativo alla directory del progetto
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Intervallo di tempo per la pulizia (es. ogni ora)
CLEANUP_INTERVAL = 3600  # Secondi (1 ora)
# Tempo massimo di vita per i file (es. 2 ore)
MAX_FILE_AGE = 7200  # Secondi (2 ore)

def cleanup_downloads():
    """
    Funzione per eliminare periodicamente i file più vecchi di MAX_FILE_AGE dalla cartella DOWNLOAD_DIR.
    """
    while True:
        try:
            now = time.time()
            for filename in os.listdir(DOWNLOAD_DIR):
                file_path = os.path.join(DOWNLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > MAX_FILE_AGE:
                        os.remove(file_path)
                        print(f"File eliminato: {filename}")
        except Exception as e:
            print(f"Errore durante la pulizia dei download: {e}")
        time.sleep(CLEANUP_INTERVAL)

# Avvia il thread di pulizia all'avvio dell'app
cleanup_thread = threading.Thread(target=cleanup_downloads)
cleanup_thread.daemon = True  # Termina con l'app
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/come-funziona')
def come_funziona():
    return render_template('info.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url', '')
    if not url:
        return jsonify({'error': 'URL mancante'}), 400
    downloader = YouTubeDownloader()
    result = downloader.analyze_url(url)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/api/download/video', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url', '')
    format_id = data.get('format_id', '')
    if not url or not format_id:
        return jsonify({'error': 'URL e formato richiesti'}), 400
    downloader = YouTubeDownloader()
    result = downloader.download_video(url, format_id, DOWNLOAD_DIR)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 400
    filename = os.path.basename(result)
    return jsonify({'file': filename, 'path': f'/download/{filename}'})

@app.route('/api/download/audio', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get('url', '')
    format_id = data.get('format_id', '')
    if not url or not format_id:
        return jsonify({'error': 'URL e formato richiesti'}), 400
    downloader = YouTubeDownloader()
    result = downloader.download_audio(url, format_id, DOWNLOAD_DIR)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 400
    filename = os.path.basename(result)
    return jsonify({'file': filename, 'path': f'/download/{filename}'})

@app.route('/api/download/subtitle', methods=['POST'])
def download_subtitle():
    data = request.get_json()
    url = data.get('url', '')
    language = data.get('language', '')
    subtitle_format = data.get('format', 'srt')
    if not url or not language:
        return jsonify({'error': 'URL e lingua richiesti'}), 400
    downloader = YouTubeDownloader()
    result = downloader.download_subtitle(url, language, subtitle_format, DOWNLOAD_DIR)
    
    # Verifica se il risultato è un dizionario con un errore
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 400
    
    # Verifica se il file esiste effettivamente
    if not os.path.exists(result):
        return jsonify({'error': f'Sottotitoli non trovati per la lingua {language}'}), 404
    
    filename = os.path.basename(result)
    return jsonify({'file': filename, 'path': f'/download/{filename}'})

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    try:
        decoded_filename = unquote(filename)
        file_path = os.path.join(DOWNLOAD_DIR, decoded_filename)
        if not os.path.exists(file_path):
            abort(404)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list_downloads', methods=['GET'])
def list_downloads():
    try:
        files = os.listdir(DOWNLOAD_DIR)
        return jsonify({'files': files})
    except Exception as e:
        print(f"Errore durante l'elenco dei download: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_download', methods=['POST'])
def delete_download():
    data = request.get_json()
    filename = data.get('filename', '')

    if not filename:
        return jsonify({'error': 'Nome del file mancante'}), 400

    # Sanifica il nome del file per prevenire attacchi di directory traversal
    decoded_filename = unquote(filename)
    file_path = os.path.join(DOWNLOAD_DIR, decoded_filename)
    
    # Assicurati che il file da eliminare sia effettivamente all'interno di DOWNLOAD_DIR
    # Questa è una misura di sicurezza critica.
    if not os.path.abspath(file_path).startswith(os.path.abspath(DOWNLOAD_DIR)):
        return jsonify({'error': 'Operazione non consentita: percorso del file non valido'}), 403

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': f'File {decoded_filename} eliminato con successo'}), 200
        else:
            return jsonify({'error': f'File {decoded_filename} non trovato'}), 404
    except Exception as e:
        print(f"Errore durante l'eliminazione del file {decoded_filename}: {e}")
        return jsonify({'error': f'Errore durante l\'eliminazione del file: {str(e)}'}), 500
