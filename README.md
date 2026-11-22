# F.R.I.D.A.Y

A Windows voice assistant that listens through the microphone, prints what it hears in the terminal, and replies out loud. The project folder is `J.A.R.V.I.S-master`, but the assistant answers to both `Friday` and `Jarvis`.

## How it runs

The app runs from the local virtual environment, not from the system Python.

```powershell
cd "C:\Users\Admin\Documents\Jarvis\J.A.R.V.I.S-master"
venv\Scripts\python.exe jarvis.py
```

Startup sequence:

1. `jarvis.py` tries face recognition through the webcam (`Face-Recognition/trainer/trainer.yml` and the Haar cascade).
2. If the camera or model is unavailable, it asks for a username/password.
3. On success, `wishMe()` greets you and the main loop starts.
4. `takeCommand()` opens the default microphone, prints `Listening...`, then `Recognizing..`, then `User said: ...`.
5. `execute_query()` matches the text to a command and `speak()` replies using Edge TTS, Windows SAPI, or eSpeak.

Speech recognition uses Google Web Speech with `en-in`, so an internet connection is required for voice commands. Recognition is synchronous: it waits for one phrase, prints it, responds, then listens again.

## Desktop shortcut

The shortcut on the Desktop is inside the `Student's Web Project` folder and is named `F.R.I.D.A.Y.lnk`. It is configured as:

| Field | Value |
| --- | --- |
| Target | `C:\Users\Admin\Documents\Jarvis\J.A.R.V.I.S-master\venv\Scripts\python.exe` |
| Arguments | `jarvis.py` |
| Start in | `C:\Users\Admin\Documents\Jarvis\J.A.R.V.I.S-master` |

To recreate it: right-click the desktop, choose **New > Shortcut**, paste the target, then append ` jarvis.py` after the target path and set the working directory in the shortcut properties.

## First-time setup

```powershell
cd "C:\Users\Admin\Documents\Jarvis\J.A.R.V.I.S-master"
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

On Windows, PyAudio may need the bundled wheel or a matching build for your Python version. The rest of the dependencies install from `requirements.txt`.

Authentication credentials are read from environment variables so no password is stored in the repository:

```powershell
$env:JARVIS_AUTH_USERNAME = "nive"
$env:JARVIS_AUTH_PASSWORD = "your-password"
```

For a permanent setup, add those variables with Windows **Edit system environment variables** or `setx`.

## Voice tests

After she says `System ready`, try these:

- `friday` or `hello friday` -> `Yes sir?`
- `what time is it`
- `tell me a joke`
- `what is the date`
- `help` -> prints the full command list on screen

If `friday` works but longer phrases do not, check the default Windows input device and microphone volume. The terminal will show `hearing audio but unclear` style messages when audio is captured but not understood.

## Commands

Time and date: `what time is it`, `tell me the time`, `what is the date`, `what day is it`.

Web and search: `open google`, `open youtube`, `open amazon`, `search youtube`, `search <query>`, `what is the location`, `wikipedia <topic>`, `sports news`, `tech news`, `news`.

Utilities: `calculate 25 plus 17`, `convert 100 dollars to euros`, `bitcoin price`, `tell me a quote`, `generate a password`, `pick a number`, `flip a coin`, `roll a dice`, `read clipboard`, `check internet`, `system status`, `diagnostics`.

System control: `volume up`, `volume down`, `mute`, `next track`, `pause`, `show desktop`, `minimize window`, `maximize window`, `disk space`, `battery status`, `top processes`, `open task manager`, `open settings`, `lock computer`, `restart`, `shutdown`.

Notes and learning: `write a note`, `read today's note`, `open note`, `remember that`, `do you remember anything`, `learn that good night means sleep well sir`, `when i say hello say hi sir`, `what did you learn`, `forget good night`.

Conversation: `how are you`, `thank you`, `say anything`, `repeat that`, `switch to male voice`, `switch to female voice`, `clear console`, `goodbye`, `sleep`.

## Speech and voice backend

- Input: `speech_recognition` using the default microphone and Google Web Speech (`en-in`).
- Output: `tts.py` tries online Edge voices first, then Windows SAPI5, then a local `bin/espeak-ng.exe` (or `JARVIS_ESPEAK_PATH`). If all fail, text is printed in the console.
- Default voice is female. Say `switch to male voice` to change it.

## Troubleshooting

Run this to check the voice engine without starting the assistant:

```powershell
venv\Scripts\python.exe -c "from tts import speak; speak('Friday online, sir')"
```

Run this to check microphone capture:

```powershell
venv\Scripts\python.exe -c "from helpers import takeCommand; print(takeCommand())"
```

Common fixes:

- No `User said:` line: select the correct microphone as the Windows default input and raise its volume.
- `Speech recognition is unavailable`: check the internet connection or Google Web Speech availability.
- Face unlock always fails: check the camera/privacy settings or press `Q` during face unlock to use the password fallback.
- No spoken audio: check the TTS backend with the command above; Edge TTS needs internet, SAPI needs Windows voices, eSpeak needs the executable.

## Project files

- `jarvis.py` - startup, authentication, main loop, command matching.
- `helpers.py` - microphone input, commands, notes, system controls, weather, conversions.
- `tts.py` - speech output with fallbacks.
- `news.py`, `youtube.py`, `youtube_downloader.py`, `OCR.py`, `diction.py`, `amazon.py` - feature modules.
- `custom_responses.json` - phrases learned at runtime.
- `data.json` - dictionary entries used by the `dictionary` command.
- `Face-Recognition/` - trainer, cascade, and helper scripts for face unlock.

## License

MIT License. See `LICENSE`.
