# Dtube: Il tuo Downloader YouTube Gratuito

![Dtube Logo](static/nome_immagine.png) Dtube è una web application intuitiva e potente sviluppata con Flask che ti permette di scaricare video e audio da YouTube in diversi formati (MP4, MP3) e qualità (HD). Progettato per essere semplice e veloce, Dtube offre un'esperienza utente fluida per ottenere i tuoi contenuti preferiti direttamente dal web.

## Caratteristiche Principali

* **Download di Video & Audio:** Scarica facilmente i tuoi video preferiti da YouTube in formato MP4 o estrai solo l'audio come MP3.
* **Qualità HD:** Supporta il download in alta definizione (HD) per un'esperienza visiva e sonora superiore.
* **Interfaccia Utente Intuitiva:** Un design pulito e reattivo che rende il processo di download semplice e immediato.
* **Selezione Formato:** Scegli tra le diverse qualità e formati video/audio disponibili per ogni contenuto.
* **Sottotitoli (Opzionale):** Funzionalità per il download dei sottotitoli disponibili (se implementata).
* **Pulizia Automatica:** I file scaricati sul server vengono eliminati automaticamente dopo un certo periodo per mantenere pulito lo spazio di archiviazione (configurabile).
* **Tecnologie Moderne:** Basato su Flask per il backend e un frontend moderno con HTML, CSS (Bootstrap) e JavaScript.

## Anteprime

Qui puoi inserire gli screenshot chiave del tuo progetto. Caricali direttamente su GitHub e poi linkali qui.

![Screenshot Pagina Principale](https://github.com/tuo-username/tuo-repo-nome/blob/main/docs/screenshot_main.png)
_Screenshot 1: La pagina principale con l'input URL._

![Screenshot Opzioni di Download](https://github.com/tuo-username/tuo-repo-nome/blob/main/docs/screenshot_download_options.png)
_Screenshot 2: Le opzioni di download video e audio disponibili dopo l'analisi._

![Screenshot Dropdown Formats](https://github.com/tuo-username/tuo-repo-nome/blob/main/docs/screenshot_dropdown_formats.png)
_Screenshot 3: Dettaglio del menu a tendina per la selezione dei formati._

## Come Funziona

1.  **Incolla il link:** Inserisci l'URL di un video YouTube nel campo di testo.
2.  **Analizza:** Clicca sul pulsante "Analizza" per recuperare le informazioni del video e i formati disponibili.
3.  **Scegli il formato:** Seleziona il formato video (MP4) o audio (MP3) desiderato dal rispettivo menu a tendina.
4.  **Scarica:** Clicca sul pulsante "Scarica" per avviare il download del file sul tuo dispositivo.

## Requisiti

Per eseguire Dtube localmente, avrai bisogno di:

* [Python](https://www.python.org/downloads/) (versione 3.8 o superiore raccomandata)
* [pip](https://pip.pypa.io/en/stable/installation/) (gestore di pacchetti per Python)
* [yt-dlp](https://github.com/yt-dlp/yt-dlp) (la libreria Python per il download da YouTube - il tuo codice usa `yt-dlp`, non `youtube-dl`)
* [FFmpeg](https://ffmpeg.org/download.html) (necessario per unire audio/video e convertire formati)

## Installazione e Avvio Locale

Segui questi passaggi per configurare ed eseguire Dtube sul tuo computer:

1.  **Clona il repository:**
    ```bash
    git clone [https://github.com/tuo-username/tuo-repo-nome.git](https://github.com/tuo-username/tuo-repo-nome.git)
    cd tuo-repo-nome
    ```
    (Sostituisci `tuo-username` e `tuo-repo-nome` con i dati effettivi del tuo repository.)

2.  **Crea un ambiente virtuale (raccomandato):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Su Linux/macOS
    # venv\Scripts\activate   # Su Windows
    ```

3.  **Installa le dipendenze Python:**
    ```bash
    pip install -r requirements.txt
    ```
    (Assicurati di avere un file `requirements.txt` nel tuo progetto che elenca tutte le dipendenze come `Flask`, `yt-dlp`, ecc.)
    Se non ce l'hai, puoi crearlo con: `pip freeze > requirements.txt`

4.  **Installa FFmpeg:**
    Scarica e installa FFmpeg dal suo [sito ufficiale](https://ffmpeg.org/download.html) e assicurati che sia accessibile nel tuo `PATH` di sistema.

5.  **Avvia l'applicazione Flask:**
    ```bash
    export FLASK_APP=app.py # O il nome del tuo file principale, se usi un'organizzazione diversa (es. run.py)
    flask run
    ```
    In alternativa, se la tua applicazione è strutturata in un modo che un file `app.py` o `run.py` la avvia direttamente:
    ```bash
    python app.py # O python run.py
    ```
    Dovresti vedere un messaggio che indica che il server è in esecuzione, di solito su `http://127.0.0.1:5000/`.

6.  **Accedi all'applicazione:**
    Apri il tuo browser e vai a `http://127.0.0.1:5000/`.

## Struttura del Progetto

Una breve panoramica della struttura delle cartelle del progetto:

```
dtube-project/
├── app/
│   ├── __init__.py      # Inizializzazione dell'app Flask (o app.py principale)
│   ├── routes.py        # Definizioni delle rotte API e delle pagine
│   └── youtube.py       # Logica per l'interazione con yt-dlp
├── templates/           # File HTML (es. index.html, info.html)
├── static/
│   ├── css/             # Fogli di stile CSS (es. style.css)
│   ├── js/              # Script JavaScript (es. main.js)
│   ├── img/             # Immagini, icone (es. nome_immagine.png, favicon.ico)
│   └── favicon.ico      # Icona del sito
├── downloads/           # Cartella dove vengono temporaneamente salvati i file scaricati
├── requirements.txt     # Dipendenze Python
└── README.md            # Questo file
```

## Contribuzioni

Le contribuzioni sono benvenute! Se trovi un bug o hai un'idea per una nuova funzionalità, sentiti libero di:

1.  Fare un fork del repository.
2.  Creare un nuovo branch (`git checkout -b feature/nuova-funzionalita`).
3.  Implementare le modifiche.
4.  Creare una Pull Request.

## Licenza

Questo progetto è distribuito sotto licenza [MIT License](LICENSE).

---
