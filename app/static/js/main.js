document.addEventListener('DOMContentLoaded', function() {
    const youtubeUrlInput = document.getElementById('youtube-url');
    const clearUrlBtn = document.getElementById('clear-url');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingElement = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const videoInfo = document.getElementById('video-info');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoTitle = document.getElementById('video-title');
    const videoUploader = document.getElementById('video-uploader');
    const videoDuration = document.getElementById('video-duration');
    const downloadVideoBtn = document.getElementById('download-video-btn');
    const downloadAudioBtn = document.getElementById('download-audio-btn');
    const videoDownloadLink = document.getElementById('video-download-link');
    const audioDownloadLink = document.getElementById('audio-download-link');

    // AGGIUNGI QUESTA RIGA: Riferimento alla sezione info
    const infoSection = document.querySelector('main .info'); // Seleziona la sezione con classe 'info' dentro 'main'

    // Custom dropdown elementi
    const videoDropdownSelected = document.getElementById('videoDropdownSelected');
    const videoDropdownMenu = document.getElementById('videoDropdownMenu');
    const videoDropdownBtn = document.getElementById('videoDropdownBtn');
    const videoDropdown = document.getElementById('video-dropdown');
    const audioDropdownSelected = document.getElementById('audioDropdownSelected');
    const audioDropdownMenu = document.getElementById('audioDropdownMenu');
    const audioDropdownBtn = document.getElementById('audioDropdownBtn');
    const audioDropdown = document.getElementById('audio-dropdown');

    let currentVideoUrl = '';
    let currentVideoFormats = [];
    let currentAudioFormats = [];
    window.selectedVideoFormat = null;
    window.selectedAudioFormat = null;

    function formatFileSize(bytes) {
        if (!bytes) return 'Dimensione sconosciuta';
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 Byte';
        const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
    }

    function formatDuration(seconds) {
        if (!seconds) return 'Durata sconosciuta';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return [
            hours > 0 ? hours : null,
            minutes,
            secs
        ]
            .filter(Boolean)
            .map(unit => unit < 10 ? `0${unit}` : `${unit}`)
            .join(':');
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
        loadingElement.classList.add('d-none');
        videoInfo.classList.add('d-none');
        // MOSTRA la sezione info in caso di errore (se vuoi)
        infoSection.classList.remove('d-none');
    }

    function hideError() {
        errorMessage.classList.add('d-none');
    }

    analyzeBtn.addEventListener('click', function() {
        const url = youtubeUrlInput.value.trim();
        if (!url) {
            showError('Inserisci un URL YouTube valido');
            return;
        }
        if (!url.match(/^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/)) {
            showError('L\'URL inserito non sembra valido');
            return;
        }
        hideError();
        videoInfo.classList.add('d-none');
        loadingElement.classList.remove('d-none');
        // NASCONDI la sezione info quando inizia l'analisi
        infoSection.classList.add('d-none'); 

        currentVideoUrl = url;
        fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ url: url }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Errore durante l\'analisi del video');
                });
            }
            return response.json();
        })
        .then(data => {
            loadingElement.classList.add('d-none');
            videoThumbnail.src = data.thumbnail;
            videoTitle.textContent = data.title;
            videoUploader.textContent = `Caricato da: ${data.uploader}`;
            videoDuration.textContent = `Durata: ${formatDuration(data.duration)}`;
            // Salva i formati per uso futuro
            currentVideoFormats = data.video_formats; // Assicurati che l'API restituisca 'video_formats'
            currentAudioFormats = data.audio_formats; // Assicurati che l'API restituisca 'audio_formats'

            // Popola i custom dropdown
            populateVideoDropdown(currentVideoFormats);
            window.selectedVideoFormat = null;
            videoDropdownSelected.textContent = 'Scegli formato';
            downloadVideoBtn.disabled = true;
            populateAudioDropdown(currentAudioFormats);
            window.selectedAudioFormat = null;
            audioDropdownSelected.textContent = 'Scegli formato';
            downloadAudioBtn.disabled = true;
            
            videoInfo.classList.remove('d-none');
            videoDownloadLink.classList.add('d-none');
            audioDownloadLink.classList.add('d-none');

            // La sezione info rimane nascosta qui, dato che il video è stato caricato
        })
        .catch(error => {
            showError(error.message);
            // In caso di errore, la sezione info dovrebbe riapparire
            infoSection.classList.remove('d-none'); 
        });
    });

    // Gestione download video con custom dropdown
    downloadVideoBtn.addEventListener('click', function() {
        const formatId = window.selectedVideoFormat;
        if (!formatId) {
            showError('Seleziona un formato video');
            return;
        }
        downloadVideoBtn.disabled = true;
        fetch('/api/download/video', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ url: currentVideoUrl, format_id: formatId }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Errore durante il download del video');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            // Avvia il download automatico senza mostrare il link
            const a = document.createElement('a');
            a.href = data.path;
            a.download = data.file;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            downloadVideoBtn.disabled = false;
            videoDownloadLink.classList.add('d-none');
        })
        .catch(error => {
            downloadVideoBtn.disabled = false;
            showError(error.message);
        });
    });

    // Gestione download audio con custom dropdown
    downloadAudioBtn.addEventListener('click', function() {
        const formatId = window.selectedAudioFormat;
        if (!formatId) {
            showError('Seleziona un formato audio');
            return;
        }
        downloadAudioBtn.disabled = true;
        fetch('/api/download/audio', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ url: currentVideoUrl, format_id: formatId }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Errore durante il download dell\'audio');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            // Avvia il download automatico senza mostrare il link
            const a = document.createElement('a');
            a.href = data.path;
            a.download = data.file;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            downloadAudioBtn.disabled = false;
            audioDownloadLink.classList.add('d-none');
        })
        .catch(error => {
            downloadAudioBtn.disabled = false;
            showError(error.message);
        });
    });

    // Funzione per popolare il custom dropdown video
    function populateVideoDropdown(formats) {
        videoDropdownMenu.innerHTML = '';
        if (!formats || formats.length === 0) {
            videoDropdownMenu.innerHTML = '<li>Nessun formato video disponibile</li>';
            videoDropdownBtn.disabled = true;
            return;
        }
        videoDropdownBtn.disabled = false;
        formats.forEach((format, idx) => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="format-type">Video</span>
                            <span class="format-detail">${format.resolution || format.format_note || 'N/A'}</span>
                            <span>${format.filesize ? formatFileSize(format.filesize) : 'Dimensione sconosciuta'}</span>
                            <span class="format-ext">${format.ext ? format.ext.toUpperCase() : 'N/A'}</span>`;
            li.dataset.formatId = format.format_id;
            li.addEventListener('click', function() {
                videoDropdownSelected.textContent = `${format.resolution || format.format_note || 'Sconosciuto'} (${format.ext || 'N/A'}) - ${format.filesize ? formatFileSize(format.filesize) : 'Dimensione sconosciuta'}`;
                videoDropdownMenu.querySelectorAll('li').forEach(el => el.classList.remove('selected'));
                li.classList.add('selected');
                window.selectedVideoFormat = format.format_id;
                videoDropdown.classList.remove('open');
                downloadVideoBtn.disabled = false;
            });
            videoDropdownMenu.appendChild(li);
        });
    }

    // Funzione per popolare il custom dropdown audio
    function populateAudioDropdown(formats) {
        audioDropdownMenu.innerHTML = '';
        // Lista estesa di formati audio supportati
        const allowedAudioExts = ['mp3', 'wav', 'aac', 'ogg', 'flac', 'm4a', 'webm', 'opus'];
        
        const filteredFormats = formats ? formats.filter(format => allowedAudioExts.includes(format.ext)) : [];

        if (filteredFormats.length === 0) {
            audioDropdownMenu.innerHTML = '<li>Nessun formato audio disponibile</li>';
            audioDropdownBtn.disabled = true;
            return;
        }
        audioDropdownBtn.disabled = false;
        
        filteredFormats.forEach((format, idx) => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="format-type">Audio</span>
                            <span class="format-detail">${format.format_note || format.ext || 'N/A'}</span>
                            <span>${format.filesize ? formatFileSize(format.filesize) : 'Dimensione sconosciuta'}</span>
                            <span class="format-ext">${format.ext ? format.ext.toUpperCase() : 'N/A'}</span>`;
            li.dataset.formatId = format.format_id;
            li.addEventListener('click', function() {
                audioDropdownSelected.textContent = `${format.format_note || format.ext || 'Sconosciuto'} (${format.ext || 'N/A'}) - ${format.filesize ? formatFileSize(format.filesize) : 'Dimensione sconosciuta'}`;
                audioDropdownMenu.querySelectorAll('li').forEach(el => el.classList.remove('selected'));
                li.classList.add('selected');
                window.selectedAudioFormat = format.format_id;
                audioDropdown.classList.remove('open');
                downloadAudioBtn.disabled = false;
            });
            audioDropdownMenu.appendChild(li);
        });
    }

    // Gestione apertura/chiusura custom dropdown video
    videoDropdownBtn.addEventListener('click', function(e) {
        videoDropdown.classList.toggle('open');
        e.stopPropagation();
    });
    // Gestione apertura/chiusura custom dropdown audio
    audioDropdownBtn.addEventListener('click', function(e) {
        audioDropdown.classList.toggle('open');
        e.stopPropagation();
    });
    // Chiudi entrambi i dropdown cliccando fuori
    document.addEventListener('click', function() {
        videoDropdown.classList.remove('open');
        audioDropdown.classList.remove('open');
    });

    // Mostra/nasconde la X in base al contenuto dell'input
    youtubeUrlInput.addEventListener('input', function() {
        if (youtubeUrlInput.value.length > 0) {
            clearUrlBtn.classList.add('show');
        } else {
            clearUrlBtn.classList.remove('show');
        }
    });
    clearUrlBtn.addEventListener('click', function() {
        youtubeUrlInput.value = '';
        clearUrlBtn.classList.remove('show');
        youtubeUrlInput.focus();
        hideError();
        videoInfo.classList.add('d-none');
        // MOSTRA di nuovo la sezione info quando il campo URL viene cancellato
        infoSection.classList.remove('d-none'); 
    });

    // Enter per analizzare
    youtubeUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeBtn.click();
        }
    });
});
