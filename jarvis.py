import wikipedia
import speech_recognition as sr
import webbrowser
import datetime
import os
import sys
import smtplib
from news import speak_news, getNewsUrl
from OCR import OCR
from diction import translate
from helpers import *
from tts import speak, set_voice, repeat_last
from youtube import youtube
from sys import platform
import os
import getpass
import cv2
import re
import time

FACE_SCAN_SECONDS = 5
AUTH_USERNAME = os.environ.get('JARVIS_AUTH_USERNAME', 'nive')
AUTH_PASSWORD = os.environ.get('JARVIS_AUTH_PASSWORD', '')

class Jarvis:
    def __init__(self) -> None:
        if platform == "linux" or platform == "linux2":
            self.chrome_path = '/usr/bin/google-chrome'

        elif platform == "darwin":
            self.chrome_path = 'open -a /Applications/Google\ Chrome.app'

        elif platform == "win32":
            self.chrome_path = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        else:
            print('Unsupported OS')
            exit(1)
        webbrowser.register(
            'chrome', None, webbrowser.BackgroundBrowser(self.chrome_path)
        )

    def wishMe(self) -> None:
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            speak("Good morning, Sir Nahom.")
        elif hour >= 12 and hour < 18:
            speak("Good afternoon, Sir Nahom.")

        else:
            speak("Good evening, Sir Nahom.")

    def sendEmail(self, to, content) -> None:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login('email', 'password')
        server.sendmail('email', to, content)
        server.close()

    def news_report(self, kind='top'):
        speak('Ofcourse sir..')
        speak_news(kind)
        speak('Do you want to read the full news...')
        if 'yes' in takeCommand().lower():
            speak('Ok sir, Opening browser...')
            webbrowser.open(getNewsUrl(kind))
            speak('You can now read the full news from this website.')
        else:
            speak('No Problem sir')

    def execute_query(self, query):
        # TODO: make this more concise
        query = (query or '').strip().lower().strip(' .,!?')
        if not query or query == 'none':
            return

        stripped = re.sub(r'^(?:hey |ok |okay )?(?:friday|jarvis)[, ]+', '', query).strip()
        if query in ('friday', 'jarvis', 'hey friday', 'hey jarvis', 'ok friday', 'okay friday'):
            speak('Yes sir?')
            return
        if re.match(r'^(hello|hi|hey|greetings)\b', query) or re.search(r'\b(hello|hi|hey)\s+(friday|jarvis)\b', query):
            speak('Yes sir?')
            return
        query = stripped or query

        if custom_response(query):
            return
        if re.search(r'\bwhat time\b|\bthe time\b|^time\b|\bcurrent time\b|\btell me the time\b', query):
            tell_time()
            return
        if 'good morning' in query:
            speak('Good morning, sir. How can I help?')
            return
        if 'good afternoon' in query:
            speak('Good afternoon, sir. How can I help?')
            return
        if 'good evening' in query:
            speak('Good evening, sir. How can I help?')
            return
        if 'good night' in query:
            speak('Good night, sir. I will be here when you need me.')
            return
        if 'what are you doing' in query:
            speak('I am actively listening for your next command, sir.')
            return
        if 'how old are you' in query:
            speak('I was created in 2021, so I am always learning, sir.')
            return
        if 'i love you' in query:
            speak('I appreciate that, sir. I am always at your service.')
            return
        if query.startswith('learn ') or query.startswith('when i say '):
            learn_response(query)
            return
        if query.startswith('forget '):
            forget_response(query)
            return
        if 'what did you learn' in query or 'what have you learned' in query or 'list learned' in query:
            list_learned()
            return

        if 'wikipedia' in query:
            speak('Searching Wikipedia....')
            query = query.replace('wikipedia', '')
            results = wikipedia.summary(query, sentences=2)
            speak('According to Wikipedia')
            print(results)
            speak(results)
        elif 'youtube downloader' in query:
            exec(open('youtube_downloader.py').read())
            
        
            
        elif 'voice' in query:
            set_voice('female' if 'female' in query else 'male')
            speak("Hello sir, I have switched my voice. How is it?")

        if 'jarvis are you there' in query or 'friday are you there' in query:
            speak("Yes sir, at your service")
        if 'jarvis who made you' in query or 'friday who made you' in query:
            speak("Yes sir, my master build me in AI")
            
         

        if query.startswith('say '):
            speak(query[4:])
        elif 'repeat' in query:
            repeat_last()
        elif 'read note' in query or 'read today' in query or "today's note" in query or 'today`s note' in query:
            read_note()
        elif 'open note' in query:
            open_note()
        elif 'write' in query or query.startswith('save '):
            write_note(query)
        elif 'how are you' in query:
            how_are_you()
        elif 'thank you' in query or 'thanks' in query:
            thank_you()
        elif 'goodbye' in query or 'good bye' in query:
            speak('Goodbye, sir.')
            sys.exit()
        elif 'clear console' in query or 'clear screen' in query:
            clear_console()
        elif 'convert' in query:
            convert(query)
        elif 'bitcoin' in query or 'ethereum' in query or 'crypto' in query:
            crypto_price(query)
        elif 'quote' in query or 'inspire' in query:
            inspire()
        elif 'password' in query:
            generate_password()
        elif 'random number' in query or 'pick a number' in query:
            random_number(query)
        elif 'clipboard' in query:
            clipboard()
        elif 'internet' in query or 'connection' in query:
            internet_status()
        elif 'diagnostic' in query:
            diagnostics()
        elif 'volume' in query or 'mute' in query:
            change_volume(query)
        elif 'next track' in query or 'previous track' in query or 'pause' in query or 'stop playback' in query or ('play' in query and 'music' not in query):
            media_control(query)
        elif 'show desktop' in query or 'minimize' in query or 'maximize' in query or 'switch window' in query or 'close window' in query:
            window_control(query)
        elif 'disk space' in query or 'free space' in query or 'storage' in query:
            disk_space()
        elif 'battery' in query:
            battery_status()
        elif 'top processes' in query or 'running processes' in query:
            running_processes()
        elif query.startswith('close ') or query.startswith('kill '):
            close_application(query)
        elif any(name in query for name in SYSTEM_TOOLS):
            open_system_tool(query)
        elif 'help' in query or 'what can you do' in query:
            show_help()

        elif 'open youtube' in query:

            webbrowser.get('chrome').open_new_tab('https://youtube.com')
            
        elif 'open amazon' in query:
            webbrowser.get('chrome').open_new_tab('https://amazon.com')

        elif 'cpu' in query:
            cpu()

        elif 'joke' in query:
            joke()

        elif 'screenshot' in query:
            speak("taking screenshot")
            screenshot()

        elif 'open google' in query:
            webbrowser.get('chrome').open_new_tab('https://google.com')

        elif 'open stackoverflow' in query:
            webbrowser.get('chrome').open_new_tab('https://stackoverflow.com')

        elif 'play music' in query:
            play_music(query)

        elif 'search youtube' in query:
            speak('What you want to search on Youtube?')
            youtube(takeCommand())
        elif 'weather' in query:
            weather(query)

        elif 'search' in query:
            speak('What do you want to search for?')
            search = takeCommand()
            url = 'https://google.com/search?q=' + search
            webbrowser.get('chrome').open_new_tab(
                url)
            speak('Here is What I found for' + search)

        elif 'location' in query:
            speak('What is the location?')
            location = takeCommand()
            url = 'https://google.nl/maps/place/' + location + '/&amp;'
            webbrowser.get('chrome').open_new_tab(url)
            speak('Here is the location ' + location)

        elif 'your master' in query:
            if platform == "win32" or "darwin":
                speak('Gaurav is my master. He created me couple of days ago')
            elif platform == "linux" or platform == "linux2":
                name = getpass.getuser()
                speak(name + ' is my master. He is running me right now')

        elif 'your name' in query:
            speak('My name is Friday')
        elif 'who made you' in query:
            speak('I was created by my AI master in 2021')
            
        elif any(word in query for word in ('calculate', 'plus', 'minus', 'times', 'divided by', 'power')) and any(character.isdigit() for character in query):
            calculate(query)
        elif 'date' in query or 'what day' in query:
            get_date()
        elif 'system status' in query or 'system report' in query:
            system_status()
        elif 'remind me' in query:
            remind_me(query)
        elif 'flip a coin' in query:
            flip_coin()
        elif 'roll a dice' in query or 'roll a die' in query:
            roll_dice()
        elif 'open notepad' in query:
            os.startfile('notepad.exe')
        elif 'open calculator' in query:
            os.startfile('calc.exe')

        elif 'stands for' in query:
            speak('Friday stands for Female Replacement Intelligent Digital Assistant Youth')
        elif 'open code' in query:
            if platform == "win32":
                os.startfile(
                    "C:\\Users\\gs935\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
            elif platform == "linux" or platform == "linux2" or "darwin":
                os.system('code .')

        elif 'shutdown' in query:
            power_control('shutdown')
        elif 'restart' in query or 'reboot' in query:
            power_control('restart')
        elif 'lock computer' in query or 'lock screen' in query or query == 'lock':
            power_control('lock')
        elif 'sleep mode' in query or 'put computer to sleep' in query:
            power_control('sleep')

        elif 'cpu' in query:
            cpu()
        elif 'your friend' in query:
            speak('My friends are Google assisstant alexa and siri')

        elif 'joke' in query:
            joke()

        elif 'screenshot' in query:
            speak("taking screenshot")
            screenshot()

        elif 'github' in query:
            webbrowser.get('chrome').open_new_tab(
                'https://github.com/gauravsingh9356')

        elif 'remember that' in query:
            speak("what should i remember sir")
            rememberMessage = takeCommand()
            speak("you said me to remember"+rememberMessage)
            remember = open('data.txt', 'w')
            remember.write(rememberMessage)
            remember.close()

        elif 'do you remember anything' in query:
            remember = open('data.txt', 'r')
            speak("you said me to remember that" + remember.read())

        elif 'sleep' in query:
            sys.exit()

        elif 'dictionary' in query:
            speak('What you want to search in your intelligent dictionary?')
            translate(takeCommand())

        elif 'sports news' in query:
            self.news_report('sports')
        elif 'tech news' in query or 'technology news' in query:
            self.news_report('tech')
        elif 'news' in query:
            self.news_report()

        elif 'voice' in query:
            set_voice('female' if 'female' in query else 'male')
            speak("Hello sir, I have switched my voice. How is it?")

        elif 'email to gaurav' in query:
            try:
                speak('What should I say?')
                content = takeCommand()
                to = 'email'
                self.sendEmail(to, content)
                speak('Email has been sent!')

            except Exception as e:
                speak('Sorry sir, Not able to send email at the moment')


def wakeUpJARVIS():
    start_listening()
    bot_ = Jarvis()
    bot_.wishMe()
    try:
        while True:
            query = takeCommand()
            if not query:
                continue
            bot_.execute_query(query)
    except KeyboardInterrupt:
        stop_listening()
        speak('Goodbye, sir.')
        sys.exit()
               

def face_authenticate(timeout=FACE_SCAN_SECONDS):
    if not hasattr(cv2, 'face'):
        print('Face recognition unavailable (opencv-contrib-python missing).')
        return False

    trainer_path = './Face-Recognition/trainer/trainer.yml'
    cascade_path = './Face-Recognition/haarcascade_frontalface_default.xml'
    if not os.path.exists(trainer_path) or not os.path.exists(cascade_path):
        print('Face recognition model not found.')
        return False

    recognizer = cv2.face.LBPHFaceRecognizer_create()  # Local Binary Patterns Histograms
    recognizer.read(trainer_path)  # load trained model
    face_cascade = cv2.CascadeClassifier(cascade_path)

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        print('Camera not available.')
        return False

    cam.set(3, 640)
    cam.set(4, 480)
    min_w = 0.1 * cam.get(3)
    min_h = 0.1 * cam.get(4)
    deadline = time.time() + timeout

    try:
        while time.time() < deadline:
            ret, img = cam.read()
            if not ret or img is None:
                print('Camera read failed.')
                return False

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(min_w), int(min_h)),
            )

            for (x, y, w, h) in faces:
                _, accuracy = recognizer.predict(gray[y:y+h, x:x+w])
                if accuracy < 100:  # lower is better, 0 is a perfect match
                    speak("Optical Face Recognition Done. Welcome")
                    return True
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)

            remaining = max(1, int(deadline - time.time()) + 1)
            cv2.putText(
                img,
                f'Face unlock: {remaining}s (press Q for password)',
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.imshow('Face Unlock', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return False
    finally:
        cam.release()
        cv2.destroyAllWindows()

    speak('Face not recognised.')
    return False


def password_auth(max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            username = input('Username: ').strip()
            password = getpass.getpass('Password: ')
        except (EOFError, KeyboardInterrupt):
            print()
            return False

        if username == AUTH_USERNAME and password == AUTH_PASSWORD:
            speak('Access granted. Welcome home, sir.')
            return True

        speak('Access denied. Please try again.')
        print(f'Invalid credentials ({attempt}/{max_attempts}).')

    return False


if __name__ == '__main__':
    if not face_authenticate():
        if not password_auth():
            speak('Access denied. Shutting down.')
            sys.exit(1)
    wakeUpJARVIS()


    
