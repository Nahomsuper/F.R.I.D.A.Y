import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

_VOICE = 'female'
_ENGINE = None
_VOICES = []
_FAILED_BACKENDS = set()
_WARNED_BACKENDS = set()
_LAST_SPOKEN = ''
_ACTIVE_BACKEND = 'console only'
_SPEAKING = threading.Event()
_SPEAK_LOCK = threading.Lock()
_BACKEND_RETRY_AFTER = {}
_LAST_SPOKE_END = 0.0
_RETRY_SECONDS = 60
_EDGE_CACHE_DIR = os.path.join(tempfile.gettempdir(), 'jarvis_tts_cache')

_BACKEND_NAMES = {
    '_speak_sapi': 'Windows SAPI5',
    '_speak_espeak': 'offline eSpeak NG',
    '_speak_edge': 'online Edge voices',
}

_EDGE_VOICES = {
    'male': 'en-US-GuyNeural',
    'female': 'en-US-JennyNeural',
}


def _find_espeak():
    candidates = [
        os.environ.get('JARVIS_ESPEAK_PATH'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'espeak-ng.exe'),
        shutil.which('espeak-ng'),
        shutil.which('espeak'),
    ]
    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _play_file(path):
    if sys.platform == 'win32' and path.lower().endswith('.wav'):
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
        return
    from playsound import playsound
    playsound(path)


def _sapi_voice_id():
    for voice in _VOICES:
        name = (getattr(voice, 'name', '') or '').lower()
        if _VOICE == 'female' and ('female' in name or 'zira' in name or 'jenny' in name):
            return voice.id
        if _VOICE == 'male' and 'female' not in name and ('male' in name or 'david' in name):
            return voice.id
    index = 1 if _VOICE == 'female' and len(_VOICES) > 1 else 0
    return _VOICES[index].id


def _speak_sapi(text):
    global _ENGINE, _VOICES
    if _ENGINE is None:
        import pyttsx3
        _ENGINE = pyttsx3.init()
        _VOICES = _ENGINE.getProperty('voices')
    if not _VOICES:
        return False
    _ENGINE.setProperty('voice', _sapi_voice_id())
    _ENGINE.setProperty('rate', 175)
    _ENGINE.say(text)
    _ENGINE.runAndWait()
    return True


def _speak_espeak(text):
    executable = _find_espeak()
    if not executable:
        return False
    handle, path = tempfile.mkstemp(suffix='.wav')
    os.close(handle)
    try:
        voice = 'en+f3' if _VOICE == 'female' else 'en+m3'
        subprocess.run(
            [executable, '-v', voice, '-w', path, text],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _play_file(path)
        return True
    finally:
        os.remove(path)


def _speak_edge(text):
    import asyncio
    import edge_tts

    os.makedirs(_EDGE_CACHE_DIR, exist_ok=True)
    key = hashlib.sha256(f'{_VOICE}|{text}'.encode('utf-8')).hexdigest()
    path = os.path.join(_EDGE_CACHE_DIR, key + '.mp3')
    if not os.path.exists(path):
        handle, temp_path = tempfile.mkstemp(suffix='.mp3')
        os.close(handle)
        try:
            async def _save():
                communicate = edge_tts.Communicate(text, _EDGE_VOICES[_VOICE])
                await asyncio.wait_for(communicate.save(temp_path), timeout=15)
            asyncio.run(_save())
            os.replace(temp_path, path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    _play_file(path)
    return True


def is_speaking():
    return _SPEAKING.is_set() or (time.time() - _LAST_SPOKE_END) < 0.4


def speak(audio):
    global _LAST_SPOKEN, _ACTIVE_BACKEND, _LAST_SPOKE_END
    text = str(audio)
    if not text.strip():
        return
    _LAST_SPOKEN = text
    with _SPEAK_LOCK:
        _SPEAKING.set()
        try:
            for backend in (_speak_edge, _speak_sapi, _speak_espeak):
                name = backend.__name__
                if name in _FAILED_BACKENDS:
                    continue
                if _BACKEND_RETRY_AFTER.get(name, 0) > time.time():
                    continue
                try:
                    if backend(text):
                        _ACTIVE_BACKEND = _BACKEND_NAMES[name]
                        return
                except Exception as error:
                    if name not in _WARNED_BACKENDS:
                        print(f'TTS: {name} unavailable ({error})')
                        _WARNED_BACKENDS.add(name)
                    if backend is _speak_sapi:
                        _FAILED_BACKENDS.add(name)
                    else:
                        _BACKEND_RETRY_AFTER[name] = time.time() + _RETRY_SECONDS
            _ACTIVE_BACKEND = 'console only'
            print(text)
        finally:
            _SPEAKING.clear()
            _LAST_SPOKE_END = time.time()


def get_backend():
    return _ACTIVE_BACKEND


def repeat_last():
    if _LAST_SPOKEN:
        speak(_LAST_SPOKEN)
    else:
        speak('I have nothing to repeat.')


def set_voice(voice):
    global _VOICE
    value = str(voice).lower()
    _VOICE = 'female' if any(name in value for name in ('female', 'friday', 'zira', 'jenny')) else 'male'
    if _ENGINE is not None and _VOICES:
        _ENGINE.setProperty('voice', _sapi_voice_id())
    return _VOICE
