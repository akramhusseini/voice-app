# Voice App — Agent Reference

## What it is

A private Flask web app for text-to-speech using the Kokoro-82M model,
accessible at `https://voice.jadeed.duckdns.org` via nginx reverse proxy.

## Service

- **Systemd unit:** `/etc/systemd/system/voice-app.service` — gunicorn, port 8445
- **Venv:** `voice-app/venv/`
- **Restart:** `sudo systemctl restart voice-app`

## File structure

```
voice-app/
├── app.py            # Flask app — all routes
├── templates/
│   └── index.html    # Main UI
├── static/
│   ├── script.js     # Frontend JS
│   └── style.css     # Styles
├── CLAUDE.md         # This file
├── requirements.txt
├── .gitignore
└── venv/             # gitignored
```

## Model

**Kokoro-82M** (hexgrad/Kokoro-82M) — 82M params, Apache license, runs on CPU.
54 voices across 9 languages (US, UK, ES, FR, HI, IT, JP, PT, CN).
Voices are downloaded on first use from HuggingFace.

## API

| Route | Method | Description |
|---|---|---|
| `/` | GET | Main UI |
| `/voices` | GET | `{voices: [{id, label, lang, gender}]}` |
| `/speak` | POST | `{text, voice?, speed?}` → `audio/wav` |
