import sounddevice as sd
import numpy as np
import speech_recognition as sr  # recognize speech
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

r = sr.Recognizer()  # initialise a recognizer

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
    api_key = "42a7f9a259d8470d9645658a8efb70c8"  # Replace with your News API key
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        news_data = response.json()
        if 'articles' in news_data:
            headlines = [article['title'] for article in news_data['articles'][:5]]
            news_summary = ". ".join(headlines)
            return news_summary
        else:
            return "Sorry, I could not fetch the news at the moment."
    except Exception as e:
        return f"An error occurred: {e}"

# Function to save schedules
def save_schedule(voice_data):
    schedule = voice_data.replace("schedule", "").strip()
    with open("schedules.txt", "a") as file:
        file.write(schedule + "\n")
    speak("Schedule saved")

speak('Welcome User!,Time to be productive')
port.write(b'p')

def respond(voice_data):
    # 1: greeting
    if there_exists(['hey', 'hi', 'hello'], voice_data):
        port.write(b'p')
        greetings = "Hey, how can I help you today?"
        speak(greetings)

    # 2: introduction
    elif there_exists(["who are you", "introduce yourself"], voice_data):
        speak("I am Billybot, your personal assistant,I can make tasks easier for you,Speak to me")

    # 3: greeting
    elif there_exists(["how are you", "how are you doing","how do you do"], voice_data):
        speak("I'm very well, thanks for asking, how are you too")

    # 4: time inquiry
    elif there_exists(["what's the time", "tell me the time", "what time is it","what says the time"], voice_data):
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
        time.sleep(2)
        if port.in_waiting > 0:
            temp_data = port.readline().decode('utf-8').strip()
            if temp_data:
                tempC, tempF, humidity = temp_data.split(',')
                speak(f"The temperature is {tempC} degrees Celsius, {tempF} degrees Fahrenheit, and the humidity is {humidity} percent.")
            else:
                speak("Sorry, I couldn't read the temperature data.")

    # 6: taking schedules
    elif there_exists(["schedule","Book a meeting"], voice_data):
        save_schedule(voice_data)
        speak("Schedule saved")

    # 7: news update
    elif there_exists(["Give me the news update", "what's the news", "tell me the news"], voice_data):
        news = get_news()
        speak(news)

    # 8: search on Wikipedia
    elif there_exists(["search for", "who is", "what is"], voice_data):
        search_term = voice_data.split("for")[-1]
        try:
            wiki_res = wiki.summary(search_term, sentences=2)
            speak(wiki_res)
        except wikipedia.exceptions.DisambiguationError:
            speak("There are multiple results for your query. Please be more specific.")
        except wikipedia.exceptions.PageError:
            speak("Sorry, I couldn't find any results for your query.")
        except wikipedia.exceptions.WikipediaException:
            speak("Sorry, I encountered an error while searching for your query.")
 # 9: google search
    elif there_exists(["search for"], voice_data) and 'youtube' not in voice_data:
        port.write(b'u')
        port.write(b'l')
        search_term = voice_data.split("for")[-1]
        url = f"https://google.com/search?q={search_term}"
        webbrowser.get().open(url)
        speak(f'Here is what I found for {search_term} on google')


    # 10: youtube search
    elif there_exists(["play"], voice_data):
        port.write(b'l')
        port.write(b'u')
        search_term = voice_data.split("play")[-1]
        url = f"https://www.youtube.com/results?search_query={search_term}"
        webbrowser.get().open(url)
        speak(f'Here is what I found for {search_term} on youtube')


    # 11: combat mode
    elif there_exists(["combat mode"], voice_data):
        speak('Unilag studio is a cutting edge innovation space located within University of Lagos')
        port.write(b'U')
        speak('Do you have an innovation idea that you have been nursing')
        port.write(b's')
        speak('Unilag design studio is the best place to transform your ideas to reality!')


    # 12: shutdown
    elif there_exists(["exit", "quit", "goodbye"], voice_data):
        speak("Goodbye for  now! Hope to speak with you again soon")
        port.write(b'u')
        exit()

time.sleep(1)
while True:
    voice_data = record_audio()  # get the voice input
    respond(voice_data)  # respond to the voice input
