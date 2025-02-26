import sounddevice as sd
import numpy as np
import speech_recognition as sr  # recognise speech
from gtts import gTTS  # google text to speech
import pyttsx3
from time import ctime  # get time details
import webbrowser  # open browser
import time
import serial  # control Arduino
import wikipedia as wiki  # Web scrapes Wikipedia content.
import tempfile
import os
import soundfile as sf
import wikipedia.exceptions
import requests  # For news updates

# Connect with UNO board over serial communication
try:
    port = serial.Serial("COM7", 9600)
    print("Physical body, connected.")
except Exception as e:
    print(f"Unable to connect to my physical body: {e}")

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def there_exists(terms, voice_data):
    for term in terms:
        if term in voice_data:
            return True
    return False

r = sr.Recognizer()  # initialise a recogniser

# Record audio from microphone
def record_audio(ask=False):
    fs = 44100  # Sample rate
    seconds = 5  # Duration of recording

    if ask:
        speak(ask)

    print("Listening...")
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    temp_file = tempfile.mktemp(suffix='.wav')
    sf.write(temp_file, recording, fs)
    
    # Recognize audio using speech recognition
    with sr.AudioFile(temp_file) as source:
        audio = r.record(source)  # read the entire audio file
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)  # convert audio to text
        except sr.UnknownValueError:  # error: recognizer does not understand
            speak('Kindly come again at the show of listening')
        except sr.RequestError:
            speak('Sorry, the service is down')  # error: recognizer is not connected
        print(f">> {voice_data.lower()}")  # print what user said
        return voice_data.lower()

# Get string and make an audio file to be played
def speak(audio_string):
    engine.say(audio_string)
    engine.runAndWait()

# Function to get news updates
def get_news():
    api_key = "YOUR_NEWS_API_KEY"  # Replace with your News API key
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    news_data = response.json()
    headlines = [article['title'] for article in news_data['articles'][:5]]
    news_summary = " ".join(headlines)
    return news_summary

# Function to save schedules
def save_schedule(voice_data):
    schedule = voice_data.replace("schedule", "").strip()
    with open("schedules.txt", "a") as file:
        file.write(schedule + "\n")
    speak("Schedule saved")

speak('Welcome User!, my name is Billybot, Time to be productive')
port.write(b'p')

def respond(voice_data):
    # 1: greeting
    if there_exists(['hey', 'hi', 'hello'], voice_data):
        port.write(b'p')
        greetings = "Hey, how can I help you Professor?"
        speak(greetings)

    # 2: introduction
    elif there_exists(["who are you", "introduce yourself"], voice_data):
        speak("I am Billybot, your personal assistant. How can I assist you today?")

    # 3: greeting
    elif there_exists(["how are you", "how are you doing"], voice_data):
        speak("I'm very well, thanks for asking Professor")

    # 4: time inquiry
    elif there_exists(["what's the time", "tell me the time", "what time is it"], voice_data):
        port.write(b'u')
        current_time = ctime().split(" ")[3].split(":")[0:2]
        if current_time[0] == "00":
            hours = '12'
        else:
            hours = current_time[0]
        minutes = current_time[1]
        time_str = f'{hours}:{minutes}'
        speak(time_str)

    # 5: temperature inquiry
    elif there_exists(["what's the temperature", "tell me the temperature"], voice_data):
        port.write(b't')

    # 6: taking schedules
    elif there_exists(["schedule"], voice_data):
        save_schedule(voice_data)

    # 7: news update
    elif there_exists(["news update", "news"], voice_data):
        news_summary = get_news()
        speak(f"Here are the top news headlines: {news_summary}")

    # 8: google search
    elif there_exists(["search for"], voice_data) and 'youtube' not in voice_data:
        port.write(b'u')
        port.write(b'l')
        search_term = voice_data.split("for")[-1]
        url = f"https://google.com/search?q={search_term}"
        webbrowser.get().open(url)
        speak(f'Here is what I found for {search_term} on google')

    # 9: youtube search
    elif there_exists(["play"], voice_data):
        port.write(b'l')
        port.write(b'u')
        search_term = voice_data.split("play")[-1]
        url = f"https://www.youtube.com/results?search_query={search_term}"
        webbrowser.get().open(url)
        speak(f'Here is what I found for {search_term} on youtube')

    # 10: wikipedia summary
    elif there_exists(['summarise', 'summarize'], voice_data):
        port.write(b'u')
        port.write(b'l')
        search_term = voice_data.split("summarize")[-1]
        try:
            summary = wiki.summary(search_term, sentences=5)
            speak(summary)
        except wikipedia.exceptions.PageError:
            speak(f"Sorry, I could not find any information on {search_term}")

    # 11: combat mode
    elif there_exists(["combat mode"], voice_data):
        speak('Thank you unilag design studio ')
        port.write(b'U')
        speak('You are the best!')
        port.write(b's')
        speak('Best innovation hub')

    # 12: shutdown
    elif there_exists(["exit", "quit", "goodbye"], voice_data):
        speak("going offline")
        port.write(b'u')
        exit()

time.sleep(1)

while True:
    voice_data = record_audio()  # get the voice input
    respond(voice_data)  # respond
