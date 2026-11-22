from tts import speak, get_backend, is_speaking
import ast
import datetime
import os
import platform
import queue
import string
import pyautogui
import psutil
import pyjokes
import random
import re
import speech_recognition as sr
import subprocess
import threading
import time
import json
import requests
from difflib import get_close_matches


def _get_location():
    if os.environ.get('JARVIS_LATITUDE') and os.environ.get('JARVIS_LONGITUDE'):
        return (
            float(os.environ['JARVIS_LATITUDE']),
            float(os.environ['JARVIS_LONGITUDE']),
            os.environ.get('JARVIS_CITY', 'your location'),
            os.environ.get('JARVIS_COUNTRY', ''),
        )
    for url in ('https://ipwho.is/', 'https://ipapi.co/json/', 'https://ipinfo.io/json'):
        try:
            info = requests.get(url, timeout=5).json()
            if 'ipwho.is' in url:
                if not info.get('success'):
                    continue
                latitude = info.get('latitude')
                longitude = info.get('longitude')
                city = info.get('city')
                country = info.get('country')
            elif 'ipapi.co' in url:
                latitude = info.get('latitude')
                longitude = info.get('longitude')
                city = info.get('city')
                country = info.get('country_name')
            else:
                latitude, longitude = info['loc'].split(',')
                city = info.get('city')
                country = info.get('country')
            if latitude is not None and longitude is not None:
                return float(latitude), float(longitude), city, country
        except Exception:
            continue
    return None, None, None, None


LATITUDE, LONGITUDE, CITY, COUNTRY = _get_location()
data = json.load(open('data.json'))


def screenshot() -> None:
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, datetime.datetime.now().strftime('screenshot_%Y%m%d_%H%M%S.png'))
    pyautogui.screenshot().save(path)
    print(path)
    speak('Screenshot saved.')


def cpu() -> None:
    speak(f'CPU is at {psutil.cpu_percent()} percent')
    battery = psutil.sensors_battery()
    if battery:
        speak(f'Battery is at {int(battery.percent)} percent')
    else:
        speak('No battery is installed.')


def joke() -> None:
    for i in range(5):
        speak(pyjokes.get_jokes()[i])


def get_date() -> None:
    speak(datetime.datetime.now().strftime('Today is %A, %d %B %Y'))


_MATH_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
    ast.USub, ast.UAdd,
)


def _math_eval(expression):
    tree = ast.parse(expression, mode='eval')
    for node in ast.walk(tree):
        if not isinstance(node, _MATH_NODES):
            raise ValueError('unsupported expression')
    return eval(compile(tree, '<calculation>', 'eval'), {'__builtins__': {}}, {})


def calculate(query) -> None:
    expression = query.lower()
    for word, symbol in (
        ('multiplied by', '*'), ('divided by', '/'), ('plus', '+'),
        ('minus', '-'), ('times', '*'), ('power', '**'),
    ):
        expression = expression.replace(word, symbol)
    expression = ''.join(
        character for character in expression
        if character.isdigit() or character in '+-*/.() '
    ).strip()
    if not expression:
        speak('I did not find a calculation in that.')
        return
    try:
        speak(f'The answer is {_math_eval(expression)}')
    except Exception:
        speak('I could not calculate that.')


def system_status() -> None:
    speak(f'CPU usage is {psutil.cpu_percent()} percent')
    speak(f'Memory usage is {psutil.virtual_memory().percent} percent')
    battery = psutil.sensors_battery()
    if battery:
        speak(f'Battery is at {int(battery.percent)} percent')
    else:
        speak('No battery is installed.')
    speak(f'Operating system is {platform.system()} {platform.release()}')


_NUMBER_WORDS = {
    'a': 1, 'an': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11,
    'twelve': 12, 'fifteen': 15, 'twenty': 20, 'thirty': 30, 'sixty': 60,
}


def remind_me(query) -> None:
    match = re.search(r'remind me (.+?) in (\w+) (second|minute|hour)s?', query.lower())
    if not match:
        speak('Say it like: remind me to drink water in five minutes.')
        return
    task, amount, unit = match.groups()
    task = task.strip()
    if task.startswith('to '):
        task = task[3:]
    try:
        amount = int(_NUMBER_WORDS.get(amount, amount))
        seconds = amount * {'second': 1, 'minute': 60, 'hour': 3600}[unit]
    except (ValueError, KeyError):
        speak('I did not understand the time for that reminder.')
        return
    unit_text = unit if amount == 1 else unit + 's'
    timer = threading.Timer(seconds, speak, [f'Reminder: {task}'])
    timer.daemon = True
    timer.start()
    speak(f'Okay sir, I will remind you to {task} in {amount} {unit_text}.')


def flip_coin() -> None:
    speak(f'You got {random.choice(["heads", "tails"])}')


def roll_dice() -> None:
    speak(f'You rolled {random.randint(1, 6)}')


def show_help() -> None:
    commands = [
        'what time is it, tell me the time, what is the date, what day is it',
        'weather, weather in London',
        'calculate 25 plus 17, or what is 12 times 5',
        'convert 100 dollars to euros, convert 30 celsius to fahrenheit',
        'bitcoin price, tell me a quote, generate a password',
        'pick a number between 1 and 10, flip a coin, roll a dice',
        'wikipedia python, news, sports news, tech news, tell me a joke',
        'search youtube, search, what is the location, read clipboard',
        'friday write hello world, write a note, read today`s note, open note',
        'learn that good night means sleep well sir, when i say hello say hi sir',
        'forget good night, what did you learn',
        'remember that, do you remember anything',
        'remind me to drink water in five minutes',
        'system status, diagnostics, check internet, how is the cpu',
        'volume up, volume down, mute, pause, next track, previous track',
        'show desktop, minimize window, maximize window, switch window, close window',
        'disk space, battery status, top processes, close application notepad',
        'open task manager, settings, control panel, device manager, services',
        'lock computer, restart computer, shutdown computer, sleep mode',
        'open google, youtube, amazon, stackoverflow, notepad, calculator',
        'take a screenshot, play music, play music by <name>, open code',
        'say anything, repeat that, how are you, thank you, goodbye',
        'clear console, switch to male voice, switch to female voice, sleep',
    ]
    print('Friday commands:')
    for command in commands:
        print(' -', command)
    speak('I can handle time and date, weather, calculations, news, Wikipedia, jokes, notes, reminders, learning new replies, system status, screenshots, opening apps and websites, and voice switching. The full list is on the screen.')


_LANGUAGE = 'en-in'
_recognizer = None
_listener = None
_audio_queue = queue.Queue()
_listener_lock = threading.Lock()


def _on_audio(recognizer, audio):
    if is_speaking():
        return
    try:
        query = recognizer.recognize_google(audio, language=_LANGUAGE)
    except sr.UnknownValueError:
        return
    except sr.RequestError as error:
        print(f'Speech recognition is unavailable: {error}')
        return
    query = query.strip()
    if query:
        print(f'User said: {query}\n')
        _audio_queue.put(query)


def start_listening():
    global _recognizer, _listener
    with _listener_lock:
        if _listener is not None:
            return _listener
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        _recognizer.pause_threshold = 0.8
        _recognizer.phrase_threshold = 0.2
        _recognizer.non_speaking_duration = 0.4
        microphone = sr.Microphone()
        try:
            with microphone as source:
                _recognizer.adjust_for_ambient_noise(source, duration=1)
            _listener = _recognizer.listen_in_background(microphone, _on_audio, phrase_time_limit=10)
            print('Active listening on. Just speak, sir.')
        except Exception as error:
            _listener = False
            print(f'Active listening unavailable: {error}')
        return _listener


def stop_listening():
    global _listener
    with _listener_lock:
        if callable(_listener):
            _listener(wait_for_stop=False)
        _listener = None


def _listen_once():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    try:
        with sr.Microphone() as source:
            print('Listening...')
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, phrase_time_limit=10)
        print('Recognizing..')
        query = recognizer.recognize_google(audio, language=_LANGUAGE)
        print(f'User said: {query}\n')
        return query
    except sr.UnknownValueError:
        print('Say that again please...')
    except sr.RequestError as error:
        print(f'Speech recognition is unavailable: {error}')
    except Exception as error:
        print(f'Microphone unavailable: {error}')
    time.sleep(0.3)
    return ''


def _drain_audio_queue():
    while True:
        try:
            _audio_queue.get_nowait()
        except queue.Empty:
            return


def takeCommand(timeout=None) -> str:
    return _listen_once()


def tell_time() -> None:
    now = datetime.datetime.now()
    spoken = now.strftime('%I:%M %p').lstrip('0')
    speak(f'It is {spoken}, sir.')


_LEARN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_responses.json')


def _load_learned():
    try:
        with open(_LEARN_PATH, encoding='utf-8') as handle:
            learned = json.load(handle)
    except Exception:
        return {}
    return {str(key).lower(): str(value) for key, value in learned.items()}


def _save_learned(learned):
    with open(_LEARN_PATH, 'w', encoding='utf-8') as handle:
        json.dump(learned, handle, indent=2, ensure_ascii=False)


def custom_response(query) -> bool:
    learned = _load_learned()
    for trigger in sorted(learned, key=len, reverse=True):
        if trigger and re.search(r'\b' + re.escape(trigger) + r'\b', query):
            speak(learned[trigger])
            return True
    return False


def learn_response(query) -> None:
    match = re.search(r'when i say (.+?)[, ]+(?:say|reply|respond)(?: with)? (.+)', query, re.I)
    if not match:
        match = re.search(r'learn (?:that )?(.+?) (?:means|is) (.+)', query, re.I)
    if not match:
        speak('Say: learn that good night means sleep well sir.')
        return
    trigger, response = (part.strip(' .,!') for part in match.groups())
    if not trigger or not response:
        speak('I need both the phrase and the answer to learn.')
        return
    learned = _load_learned()
    learned[trigger.lower()] = response
    _save_learned(learned)
    speak(f'Learned. When you say {trigger}, I will reply {response}.')


def forget_response(query) -> None:
    match = re.search(r'forget (?:that )?(.+)', query, re.I)
    trigger = match.group(1).strip(' .,!').lower() if match else ''
    learned = _load_learned()
    if trigger in learned:
        del learned[trigger]
        _save_learned(learned)
        speak(f'Okay, I forgot {trigger}.')
    else:
        speak('I have not learned that phrase.')


def list_learned() -> None:
    learned = _load_learned()
    if not learned:
        speak('You have not taught me anything yet.')
        return
    print('Learned responses:')
    for trigger, response in learned.items():
        print(f'  {trigger} -> {response}')
    speak(f'I know {len(learned)} learned phrases. They are on the screen.')

WEATHER_CODES = {
    0: 'clear sky',
    1: 'mainly clear',
    2: 'partly cloudy',
    3: 'overcast',
    45: 'foggy',
    48: 'rime fog',
    51: 'light drizzle',
    53: 'moderate drizzle',
    55: 'dense drizzle',
    61: 'slight rain',
    63: 'moderate rain',
    65: 'heavy rain',
    71: 'slight snow',
    73: 'moderate snow',
    75: 'heavy snow',
    77: 'snow grains',
    80: 'slight rain showers',
    81: 'moderate rain showers',
    82: 'violent rain showers',
    85: 'slight snow showers',
    86: 'heavy snow showers',
    95: 'thunderstorm',
    96: 'thunderstorm with hail',
    99: 'thunderstorm with heavy hail',
}


def weather(query=''):
    latitude, longitude, city, country = LATITUDE, LONGITUDE, CITY, COUNTRY
    match = re.search(r'\b(?:in|for|at|of)\s+([A-Za-z][A-Za-z .,\-]{1,60})', query or '', re.I)
    if match:
        place = match.group(1).strip(' .,?')
        try:
            lookup = requests.get(
                'https://geocoding-api.open-meteo.com/v1/search',
                params={'name': place, 'count': 1, 'language': 'en', 'format': 'json'},
                timeout=10,
            )
            results = lookup.json().get('results') or []
            if results:
                found = results[0]
                latitude, longitude = found['latitude'], found['longitude']
                city = found.get('name', place)
                country = found.get('country', '')
            else:
                speak(f'I could not find {place}.')
        except Exception:
            speak(f'Location lookup failed for {place}.')

    if latitude is None or longitude is None:
        speak('Location is unavailable, so I cannot get the weather.')
        return

    response = requests.get(
        'https://api.open-meteo.com/v1/forecast',
        params={
            'latitude': latitude,
            'longitude': longitude,
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
        },
        timeout=15,
    )
    response.raise_for_status()
    current = response.json()['current']
    description = WEATHER_CODES.get(current['weather_code'], 'unknown conditions')

    speak(f"Location is {city}, {country}")
    speak(f"Latitude {round(latitude, 2)} and longitude {round(longitude, 2)}")
    speak(f"Weather is {description}")
    speak(f"Temperature is {current['temperature_2m']} degrees Celsius")
    speak(f"Wind speed is {current['wind_speed_10m']} kilometres per hour")
    speak(f"Humidity is {current['relative_humidity_2m']} percent")


def translate(word):
    word = word.lower()
    if word in data:
        speak(data[word])
    elif len(get_close_matches(word, data.keys())) > 0:
        x = get_close_matches(word, data.keys())[0]
        speak('Did you mean ' + x +
              ' instead,  respond with Yes or No.')
        ans = takeCommand().lower()
        if 'yes' in ans:
            speak(data[x])
        elif 'no' in ans:
            speak("Word doesn't exist. Please make sure you spelled it correctly.")
        else:
            speak("We didn't understand your entry.")

    else:
        speak("Word doesn't exist. Please double check it.")


CURRENCIES = {
    'dollar': 'USD', 'dollars': 'USD', 'usd': 'USD',
    'euro': 'EUR', 'euros': 'EUR', 'eur': 'EUR',
    'pound': 'GBP', 'pounds': 'GBP', 'gbp': 'GBP',
    'yen': 'JPY', 'jpy': 'JPY',
    'rupee': 'INR', 'rupees': 'INR', 'inr': 'INR',
    'birr': 'ETB', 'birrs': 'ETB', 'etb': 'ETB',
    'franc': 'CHF', 'francs': 'CHF',
    'yuan': 'CNY', 'renminbi': 'CNY', 'cny': 'CNY',
}

_UNITS = {
    'temperature': {
        'c': 'celsius', 'celsius': 'celsius',
        'f': 'fahrenheit', 'fahrenheit': 'fahrenheit',
    },
    'length': {
        'km': 1.0, 'kilometer': 1.0, 'kilometers': 1.0, 'kilometre': 1.0, 'kilometres': 1.0,
        'm': 0.001, 'meter': 0.001, 'meters': 0.001, 'metre': 0.001, 'metres': 0.001,
        'cm': 0.00001, 'centimeter': 0.00001, 'centimeters': 0.00001,
        'mi': 1.609344, 'mile': 1.609344, 'miles': 1.609344,
        'ft': 0.0003048, 'foot': 0.0003048, 'feet': 0.0003048,
        'inch': 0.0000254, 'inches': 0.0000254,
    },
    'weight': {
        'kg': 1.0, 'kilogram': 1.0, 'kilograms': 1.0,
        'g': 0.001, 'gram': 0.001, 'grams': 0.001,
        'lb': 0.45359237, 'lbs': 0.45359237, 'pound': 0.45359237, 'pounds': 0.45359237,
        'oz': 0.0283495, 'ounce': 0.0283495, 'ounces': 0.0283495,
    },
}


def convert(query) -> None:
    match = re.search(r'(\d+(?:\.\d+)?)\s+([a-zA-Z°]+)\s+(?:to|into|in)\s+([a-zA-Z°]+)', query.lower())
    if not match:
        speak('Say it like: convert 100 dollars to euros.')
        return
    amount_text, source, target = match.groups()
    amount = float(amount_text)
    source = source.strip('°')
    target = target.strip('°')

    if source in CURRENCIES and target in CURRENCIES:
        try:
            response = requests.get(
                'https://api.frankfurter.app/latest',
                params={'from': CURRENCIES[source], 'to': CURRENCIES[target]},
                timeout=10,
            )
            response.raise_for_status()
            rate = response.json()['rates'][CURRENCIES[target]]
            speak(f'{amount_text} {source} is {round(amount * rate, 2)} {target}.')
        except Exception:
            speak('Currency conversion is unavailable right now.')
        return

    temperatures = _UNITS['temperature']
    if source in temperatures and target in temperatures:
        source_name = temperatures[source]
        target_name = temperatures[target]
        if source_name == target_name:
            result = amount
        elif source_name == 'celsius':
            result = amount * 9 / 5 + 32
        else:
            result = (amount - 32) * 5 / 9
        speak(f'{amount_text} {source} is {round(result, 2)} {target}.')
        return

    for table in (_UNITS['length'], _UNITS['weight']):
        if source in table and target in table:
            result = amount * table[source] / table[target]
            speak(f'{amount_text} {source} is {round(result, 4)} {target}.')
            return
    speak('I cannot convert those units.')


def crypto_price(query) -> None:
    name = 'ethereum' if 'ethereum' in query.lower() or 'eth' in query.lower() else 'bitcoin'
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': name, 'vs_currencies': 'usd'},
            timeout=10,
        )
        response.raise_for_status()
        price = response.json()[name]['usd']
        speak(f'{name.title()} is {price} dollars')
    except Exception:
        speak('Crypto prices are unavailable right now.')


def inspire() -> None:
    try:
        response = requests.get('https://zenquotes.io/api/random', timeout=10)
        response.raise_for_status()
        quote = response.json()[0]
        print(f'"{quote["q"]}" - {quote["a"]}')
        speak(f'{quote["q"]} By {quote["a"]}')
    except Exception:
        speak('I could not fetch a quote right now.')


def generate_password() -> None:
    characters = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(random.SystemRandom().choice(characters) for _ in range(16))
    print('Generated password:', password)
    speak('I generated a strong password. It is on the screen.')


def random_number(query) -> None:
    match = re.search(r'(\d+)\s*(?:and|to|-)\s*(\d+)', query)
    low, high = (int(match.group(1)), int(match.group(2))) if match else (1, 10)
    if low > high:
        low, high = high, low
    speak(f'I picked {random.randint(low, high)}')


def clipboard() -> None:
    try:
        import pyperclip
        text = pyperclip.paste().strip()
        if text:
            print('Clipboard:', text)
            speak('Clipboard contents are on the screen.')
        else:
            speak('Clipboard is empty.')
    except Exception:
        speak('Clipboard is unavailable.')


def internet_status() -> None:
    try:
        requests.get('https://www.google.com', timeout=5)
        speak('Internet connection is working.')
    except Exception:
        speak('Internet appears to be offline.')


def diagnostics() -> None:
    speak(f'Voice engine: {get_backend()}')
    speak(f'CPU usage is {psutil.cpu_percent()} percent')
    speak(f'Memory usage is {psutil.virtual_memory().percent} percent')
    if os.name == 'nt':
        disk = psutil.disk_usage('C:\\')
        speak(f'Disk usage is {int(disk.percent)} percent')
    internet_status()


def how_are_you() -> None:
    speak('I am functioning perfectly, sir. Ready for your commands.')


def thank_you() -> None:
    speak('You are welcome, sir.')


def clear_console() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def play_music(query='') -> None:
    folder = os.path.join(os.path.expanduser('~'), 'Music')
    term = ''
    match = re.search(r'play music(?: by| for)?\s+(.+)', (query or '').lower())
    if match:
        term = match.group(1).strip()
    matches = []
    if os.path.isdir(folder):
        matches = [
            name for name in os.listdir(folder)
            if name.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg'))
            and (not term or term in name.lower())
        ]
    if not matches:
        speak('I could not find that music in your Music folder.')
        return
    choice = random.choice(matches)
    os.startfile(os.path.join(folder, choice))
    speak(f'Playing {choice}')


SYSTEM_TOOLS = {
    'task manager': 'taskmgr.exe',
    'control panel': 'control.exe',
    'device manager': 'devmgmt.msc',
    'file explorer': 'explorer.exe',
    'command prompt': 'cmd.exe',
    'powershell': 'powershell.exe',
    'disk management': 'diskmgmt.msc',
    'event viewer': 'eventvwr.msc',
    'services': 'services.msc',
    'settings': 'ms-settings:',
}


def open_system_tool(query):
    for name, command in SYSTEM_TOOLS.items():
        if name in query:
            try:
                if command.startswith('ms-settings:'):
                    os.startfile(command)
                else:
                    subprocess.Popen(command, shell=False)
                speak(f'Opening {name}')
            except Exception:
                speak(f'I could not open {name}.')
            return
    speak('I did not recognise that system tool.')


def change_volume(query):
    if 'mute' in query:
        pyautogui.press('volumemute')
        speak('Volume muted.')
        return
    direction = 'down' if any(word in query for word in ('down', 'lower', 'decrease')) else 'up'
    pyautogui.press('volumeup' if direction == 'up' else 'volumedown')
    speak(f'Volume {direction}.')


def media_control(query):
    if 'next' in query:
        pyautogui.press('nexttrack')
        action = 'Next track'
    elif 'previous' in query or 'back' in query:
        pyautogui.press('prevtrack')
        action = 'Previous track'
    elif 'stop' in query:
        pyautogui.press('stop')
        action = 'Playback stopped'
    else:
        pyautogui.press('playpause')
        action = 'Play or pause'
    speak(action)


def window_control(query):
    if 'show desktop' in query or 'minimize all' in query:
        pyautogui.hotkey('win', 'd')
        action = 'Showing desktop'
    elif 'switch' in query:
        pyautogui.hotkey('alt', 'tab')
        action = 'Switching window'
    elif 'close window' in query:
        pyautogui.hotkey('alt', 'f4')
        action = 'Closing window'
    elif 'maximize' in query:
        pyautogui.hotkey('win', 'up')
        action = 'Maximizing window'
    elif 'minimize' in query:
        pyautogui.hotkey('win', 'down')
        action = 'Minimizing window'
    else:
        speak('I did not recognise that window command.')
        return
    speak(action)


def power_control(action):
    commands = {
        'shutdown': (['shutdown', '/s', '/t', '5'], 'Shutting down in five seconds.'),
        'restart': (['shutdown', '/r', '/t', '5'], 'Restarting in five seconds.'),
        'lock': (['rundll32.exe', 'user32.dll,LockWorkStation'], 'Locking the computer.'),
        'sleep': (['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], 'Putting the computer to sleep.'),
    }
    command, message = commands[action]
    speak(message)
    try:
        subprocess.Popen(command, shell=False)
    except Exception:
        speak('I could not run that power command.')


def disk_space():
    drive = 'C:\\' if os.name == 'nt' else '/'
    disk = psutil.disk_usage(drive)
    total = round(disk.total / (1024 ** 3))
    free = round(disk.free / (1024 ** 3))
    speak(f'Disk has {free} gigabytes free out of {total}. {int(disk.percent)} percent is used.')


def battery_status():
    battery = psutil.sensors_battery()
    if not battery:
        speak('No battery is installed.')
        return
    state = 'charging' if battery.power_plugged else 'running on battery'
    speak(f'Battery is at {int(battery.percent)} percent and {state}.')


def running_processes():
    try:
        processes = sorted(
            psutil.process_iter(['name', 'cpu_percent']),
            key=lambda item: item.info['cpu_percent'] or 0,
            reverse=True,
        )[:5]
        print('Top processes by CPU:')
        for process in processes:
            print(f"  {process.info['name']}: {process.info['cpu_percent']}%")
        speak('Top processes are on the screen.')
    except Exception:
        speak('I could not read the process list.')


def close_application(query):
    name = re.split(r'close|kill|stop', query, maxsplit=1, flags=re.I)[-1]
    for word in ('application', 'app', 'program', 'process', 'the', 'please'):
        name = re.sub(r'\b' + word + r'\b', '', name, flags=re.I)
    name = name.strip(' .')
    if not name:
        speak('Tell me which application to close.')
        return
    closed = 0
    for process in psutil.process_iter(['name']):
        if process.pid == os.getpid():
            continue
        try:
            if name.lower() in (process.info['name'] or '').lower():
                process.terminate()
                closed += 1
        except Exception:
            continue
    if closed:
        speak(f'Closed {closed} process or processes matching {name}.')
    else:
        speak(f'I did not find {name} running.')


def _note_path():
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    os.makedirs(desktop, exist_ok=True)
    return os.path.join(desktop, datetime.datetime.now().strftime('%Y-%m-%d') + '.txt')


def write_note(query='') -> None:
    parts = re.split(r'\b(?:write|save|note|down)\b', query or '', maxsplit=1, flags=re.I)
    content = parts[-1].strip(' .') if len(parts) > 1 else ''
    if not content or content.lower() in ('it', 'this', 'that', 'a', 'the'):
        speak('What should I write?')
        content = takeCommand()
    if not content or content.lower() == 'none':
        speak('I did not catch the text.')
        return
    path = _note_path()
    existing = os.path.exists(path) and os.path.getsize(path) > 0
    with open(path, 'a', encoding='utf-8') as note:
        if existing:
            note.write('\n--- ' + datetime.datetime.now().strftime('%H:%M:%S') + ' ---\n')
        note.write(content.strip() + '\n')
    print('Saved:', path)
    speak('Saved your note to ' + os.path.basename(path) + ' on the desktop.')


def read_note() -> None:
    path = _note_path()
    if not os.path.exists(path):
        speak('There is no note for today.')
        return
    text = open(path, encoding='utf-8').read().strip()
    if not text:
        speak('Today`s note is empty.')
        return
    print(text)
    if len(text) < 300:
        speak('Your note says: ' + text)
    else:
        speak('Your note is on the screen.')


def open_note() -> None:
    path = _note_path()
    if not os.path.exists(path):
        speak('There is no note for today.')
        return
    os.startfile(path)
    speak('Opening today`s note.')
