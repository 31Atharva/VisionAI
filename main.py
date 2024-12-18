import pyttsx3
import speech_recognition as sr
import datetime
import time
import webbrowser
import pyautogui  # for controlling the system volume
import sys

import json
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import random
import numpy as np
import os
import psutil
import subprocess


with open("intents.json") as file:
    data = json.load(file)

model = load_model("chat_model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer=pickle.load(f)

with open("label_encoder.pkl", "rb") as encoder_file:
    label_encoder=pickle.load(encoder_file)


def initialize_engine():
    # Use 'nsss' driver for macOS
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)  # Adjust speaking rate
    
    volume = engine.getProperty('volume')
    engine.setProperty('volume', min(volume + 0.25, 1.0))  # Ensure volume doesn't exceed 1.0
    
    return engine
def speak(text):
    engine = initialize_engine()
    engine.say(text)
    engine.runAndWait()


def command():
    r = sr.Recognizer()

    # List available microphones if unsure
    # for i, microphone in enumerate(sr.Microphone.list_microphone_names()):
    #     print(f"Microphone {i}: {microphone}")

    mic_index = 0  # Adjust this index based on your available microphone
    with sr.Microphone(device_index=mic_index) as source:
        print("Adjusting for ambient noise... Please wait.")
        r.adjust_for_ambient_noise(source, duration=0.5)  # Adjusting for ambient noise
        print("Listening... Speak now!")

        # Set other parameters
        r.pause_threshold = 1.0
        r.phrase_threshold = 0.3
        r.sample_rate = 48000
        r.dynamic_energy_threshold = True
        r.operation_timeout = 5
        r.non_speaking_duration = 0.5
        r.dynamic_energy_adjustment = 2
        r.energy_threshold = 4000
        r.phrase_time_limit = 10

        try:
            audio = r.listen(source, timeout=5)  # Set a timeout of 5 seconds
        except sr.WaitTimeoutError:
            print("Listening timeout. No audio detected.")
            return "None"  # Return None if timeout occurs
        except Exception as e:
            print("Error while listening:", e)
            return "None"

    try:
        print("\r", end="", flush=True)
        print("Recognizing...", end="", flush=True)
        query = r.recognize_google(audio, language='en-in')  # Recognize speech using Google's API
        print("\r", end="", flush=True)
        print(f"User said: {query}\n")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
        return "None"
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return "None"
    except Exception as e:
        print("Error during recognition:", e)
        return "None"

    return query


def cal_day():
    day = datetime.datetime.today().weekday() + 1
    day_dict = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    return day_dict.get(day, "Unknown")


def wishMe():
    hour = int(datetime.datetime.now().hour)
    t = time.strftime("%I:%M:%p")
    day = cal_day()

    if hour >= 0 and hour <= 12 and 'AM' in t:
        speak(f"Good morning Atharva, it's {day} and the time is {t}")
    elif hour >= 12 and hour <= 16 and 'PM' in t:
        speak(f"Good afternoon Atharva, it's {day} and the time is {t}")
    else:
        speak(f"Good evening Atharva, it's {day} and the time is {t}")

def social_media(command):
    if 'facebook' in command:
        speak("Opening your Facebook")
        webbrowser.open("https://www.facebook.com/")
    elif 'discord' in command:
        speak("Opening Discord")
        webbrowser.open("https://discord.com/")
    elif 'whatsapp' in command:
        speak("Opening WhatsApp")
        webbrowser.open("https://web.whatsapp.com/")
    elif 'instagram' in command:
        speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com/")

def schedule():
    day = cal_day().lower()
    speak("Boss today's schedule is ")
    week={
    "monday": "Boss, from 9:00 to 9:50 you have Algorithms class, from 10:00 to 11:50 you have System Design class, from 12:00 to 2:00 you have a break, and today you have Programming Lab from 2:00 onwards.",
    "tuesday": "Boss, from 9:00 to 9:50 you have Web Development class, from 10:00 to 10:50 you have a break, from 11:00 to 12:50 you have Database Systems class, from 1:00 to 2:00 you have a break, and today you have Open Source Projects lab from 2:00 onwards.",
    "wednesday": "Boss, today you have a full day of classes. From 9:00 to 10:50 you have Machine Learning class, from 11:00 to 11:50 you have Operating Systems class, from 12:00 to 12:50 you have Ethics in Technology class, from 1:00 to 2:00 you have a break, and today you have Software Engineering workshop from 2:00 onwards.",
    "thursday": "Boss, today you have a full day of classes. From 9:00 to 10:50 you have Computer Networks class, from 11:00 to 12:50 you have Cloud Computing class, from 1:00 to 2:00 you have a break, and today you have Cybersecurity lab from 2:00 onwards.",
    "friday": "Boss, today you have a full day of classes. From 9:00 to 9:50 you have Artificial Intelligence class, from 10:00 to 10:50 you have Advanced Programming class, from 11:00 to 12:50 you have UI/UX Design class, from 1:00 to 2:00 you have a break, and today you have Capstone Project work from 2:00 onwards.",
    "saturday": "Boss, today you have a more relaxed day. From 9:00 to 11:50 you have team meetings for your Capstone Project, from 12:00 to 12:50 you have Innovation and Entrepreneurship class, from 1:00 to 2:00 you have a break, and today you have extra time to work on personal development and coding practice from 2:00 onwards.",
    "sunday": "Boss, today is a holiday, but keep an eye on upcoming deadlines and use this time to catch up on any reading or project work."
    }
    if day in week.keys():
        speak(week[day])


def openApp(command):
    try:
        if "calculator" in command:
            speak("Opening Calculator")
            subprocess.run(["open", "-a", "Calculator"], check=True)
        elif "notes" in command:
            speak("Opening Notes")
            subprocess.run(["open", "-a", "Notes"], check=True)
        elif "safari" in command:
            speak("Opening Safari")
            subprocess.run(["open", "-a", "Safari"], check=True)
        else:
            speak("Sorry, I couldn't recognize the application.")
    except subprocess.CalledProcessError:
        speak("Failed to open the application.")
        print("Error opening the application.")

def closeApp(command):
    try:
        if "calculator" in command:
            speak("Closing Calculator")
            subprocess.run(["osascript", "-e", 'quit app "Calculator"'], check=True)
        elif "notes" in command:
            speak("Closing Notes")
            subprocess.run(["osascript", "-e", 'quit app "Notes"'], check=True)
        elif "safari" in command:
            speak("Closing Safari")
            subprocess.run(["osascript", "-e", 'quit app "Safari"'], check=True)
        else:
            speak("Sorry, I couldn't recognize the application.")
    except subprocess.CalledProcessError:
        speak("Failed to close the application.")
        print("Error closing the application.")

    import webbrowser

def browsing(query):
    if 'google' in query:
        speak("Boss, what should I search on Google?")
        s = command().lower()
        if s != "none":  # Check if speech recognition failed
            search_url = f"https://www.google.com/search?q={s.replace(' ', '+')}"
            speak(f"Searching Google for {s}")
            webbrowser.open(search_url)  # Open in the default browser
        else:
            speak("I couldn't understand what to search. Please try again.") 


def condition():
    # CPU usage
    usage = str(psutil.cpu_percent(interval=1))  # CPU percentage
    speak(f"CPU is at {usage} percent")

    # Battery check using macOS 'pmset' command
    try:
        battery_info = subprocess.check_output(["pmset", "-g", "batt"]).decode("utf-8")
        battery_line = battery_info.splitlines()[1]  # Extract the relevant line
        percentage = int(battery_line.split('\t')[1].split('%')[0])  # Get battery percentage

        speak(f"Boss, our system has {percentage} percent battery remaining.")

        if percentage >= 80:
            speak("Boss, we have enough charge to continue our recording.")
        elif 40 <= percentage <= 75:
            speak("Boss, we should connect our system to a charging point to charge our battery.")
        else:
            speak("Boss, we have very low power. Please connect to charging, otherwise recording will stop.")
    except Exception as e:
        speak("Boss, I am unable to fetch the battery status on your system.")
        print(f"Error: {e}")

# Test the functions
if __name__ == "__main__":
    wishMe()
    while True:
        query = command().lower()

        if ('facebook' in query) or ('discord' in query) or ('whatsapp' in query) or ('instagram' in query):
            social_media(query)
        elif ("university time table" in query) or ("schedule" in query):
            schedule()
        elif ("volume up" in query) or ("increase volume" in query):
            pyautogui.press("volumeup")
            speak("Volume increased")
        elif ("volume down" in query) or ("decrease volume" in query):
            pyautogui.press("volumedown")
            speak("Volume decreased")
        elif ("volume mute" in query) or ("mute the sound" in query):
            pyautogui.press("volumemute")
            speak("Volume muted")
        elif ("open calculator" in query) or ("open notes" in query) or ("open safari" in query) :
            openApp(query)
        elif ("close calculator" in query) or ("close notes" in query) or ("close safari" in query):
            closeApp(query)
        elif ("what" in query) or ("who" in query) or ("how" in query) or ("hi" in query) or ("thanks" in query) or ("hello" in query):
                padded_sequences = pad_sequences(tokenizer.texts_to_sequences([query]), maxlen=20, truncating='post')
                result = model.predict(padded_sequences)
                tag = label_encoder.inverse_transform([np.argmax(result)])

                for i in data['intents']:
                    if i['tag'] == tag:
                        speak(np.random.choice(i['responses']))
        elif ("open google" in query):
            browsing(query)
        elif ("system condition" in query) or ("condition of the system" in query):
            speak("checking the system condition")
            condition()
        elif "exit" in query:
            sys.exit()