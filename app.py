import io
import json
import logging
import os
import sys
import tempfile
import traceback

import soundfile as sf
from flask import Flask, jsonify, render_template, request, send_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', stream=sys.stdout)
log = logging.getLogger('voice-app')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

# ── Kokoro pipeline (lazy-loaded) ──
_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        from kokoro import KPipeline
        log.info("Loading Kokoro-82M pipeline…")
        _pipeline = KPipeline(lang_code='a')
        log.info("Kokoro-82M pipeline ready")
    return _pipeline


_VOICES_CACHE = None


def _list_voices():
    global _VOICES_CACHE
    if _VOICES_CACHE is None:
        from huggingface_hub import HfApi
        api = HfApi()
        files = api.list_repo_files('hexgrad/Kokoro-82M')
        voices = sorted(f for f in files if f.startswith('voices/') and f.endswith('.pt'))
        _VOICES_CACHE = []
        for v in voices:
            name = v.replace('voices/', '').replace('.pt', '')
            # Decode voice metadata from naming
            lang_map = {'a': 'US', 'b': 'UK', 'e': 'ES', 'f': 'FR', 'h': 'HI',
                        'i': 'IT', 'j': 'JP', 'p': 'PT', 'z': 'CN'}
            gender = 'Female' if name[1] == 'f' else 'Male'
            lang = lang_map.get(name[0], name[0])
            display = name[3:].replace('_', ' ').title()
            _VOICES_CACHE.append({
                'id': name,
                'label': f"{display} ({lang}, {gender})",
                'lang': lang,
                'gender': gender,
            })
    return _VOICES_CACHE


# ── Routes ──

@app.route('/')
def index():
    return render_template('index.html', voices=json.dumps(_list_voices()))


@app.route('/voices')
def voices():
    return jsonify({'voices': _list_voices()})


@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    voice = (data.get('voice') or 'af_heart').strip()
    speed = float(data.get('speed', 1.0))

    try:
        p = _get_pipeline()
        gen = p(text, voice=voice, speed=speed)
        chunks = [g.audio for g in gen]
        if not chunks:
            return jsonify({'error': 'No audio generated'}), 500
        import numpy as np
        audio = np.concatenate(chunks)

        buf = io.BytesIO()
        sf.write(buf, audio, 24000, format='WAV')
        buf.seek(0)
        return send_file(buf, mimetype='audio/wav')
    except Exception as e:
        log.error("TTS failed: %s", traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8445))
    log.info(f"Starting dev server on {host}:{port}")
    app.run(host=host, port=port, threaded=True)
