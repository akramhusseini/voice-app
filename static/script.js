let _lastAudioUrl = null;
let _voices = [];

function init() {
    const voicesEl = document.getElementById('voice-select');
    const voiceCountEl = document.getElementById('voice-count');

    try {
        _voices = JSON.parse(voicesEl.dataset.voices || '[]');
    } catch(e) {}

    if (!_voices.length) {
        fetch('/voices')
            .then(r => r.json())
            .then(data => {
                _voices = data.voices || [];
                populateVoices(voicesEl, _voices);
                voiceCountEl.textContent = _voices.length + ' voices';
            });
    } else {
        populateVoices(voicesEl, _voices);
        voiceCountEl.textContent = _voices.length + ' voices';
    }

    document.getElementById('text-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            speak();
        }
    });
}

function populateVoices(el, voices) {
    el.innerHTML = voices.map(v =>
        `<option value="${v.id}">${v.label}</option>`
    ).join('');
}

function speak() {
    const text = document.getElementById('text-input').value.trim();
    if (!text) {
        setStatus('Please enter some text', 'is-error');
        return;
    }

    const voice = document.getElementById('voice-select').value;
    const speed = document.getElementById('speed-select').value;
    const btn = document.getElementById('speak-btn');
    const status = document.getElementById('status');

    btn.disabled = true;
    setStatus('Generating…', 'is-active');

    fetch('/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice, speed }),
    })
    .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.error || r.statusText); });
        return r.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        if (_lastAudioUrl) URL.revokeObjectURL(_lastAudioUrl);
        _lastAudioUrl = url;

        const player = document.getElementById('player');
        player.src = url;

        document.getElementById('player-card').style.display = 'flex';
        setStatus('Done', '');
        btn.disabled = false;
    })
    .catch(err => {
        setStatus('Error: ' + err.message, 'is-error');
        btn.disabled = false;
    });
}

function downloadAudio() {
    const player = document.getElementById('player');
    if (!player.src) return;
    const a = document.createElement('a');
    a.href = player.src;
    a.download = 'voice.wav';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function setStatus(msg, cls) {
    const el = document.getElementById('status');
    el.textContent = msg;
    el.className = 'status' + (cls ? ' ' + cls : '');
}

document.addEventListener('DOMContentLoaded', init);
