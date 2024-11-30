import openai
import speech_recognition as sr
import pyttsx3
import webbrowser
import time
import os
import subprocess
import requests  # To handle API requests for weather forecasts

# Initialize OpenAI API
openai.api_key = 'api key from gpt'

# Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Add your OpenWeatherMap API key here
weather_api_key = 'your_openweather_api_key'


def respond_jarvis(response):
    print(f"Jarvis: {response}")
    engine.say(response)
    engine.runAndWait()


# Function to get weather forecast for a city
def get_weather_forecast(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={weather_api_key}&units=metric"

    try:
        response = requests.get(complete_url)
        weather_data = response.json()

        if weather_data["cod"] != "404":
            main = weather_data["main"]
            weather_desc = weather_data["weather"][0]["description"]
            temperature = main["temp"]
            humidity = main["humidity"]
            wind_speed = weather_data["wind"]["speed"]
            forecast = (f"The current temperature in {city} is {temperature}°C, "
                        f"with {weather_desc}. The humidity is {humidity}% "
                        f"and wind speed is {wind_speed} meters per second.")
        else:
            forecast = f"Sorry, I couldn't find weather information for {city}."
    except Exception as e:
        forecast = "Sorry, I couldn't retrieve the weather data right now."

    return forecast


# Function to open folders (same as before)
def open_folder(query):
    folder_path = {
        "documents": "C:/Users/YourUsername/Documents",
        "downloads": "C:/Users/YourUsername/Downloads",
        "desktop": "C:/Users/YourUsername/Desktop",
        "pictures": "C:/Users/YourUsername/Pictures"
    }

    for folder_name, path in folder_path.items():
        if folder_name in query.lower():
            if os.path.exists(path):
                os.startfile(path)
                respond_jarvis(f"Opening {folder_name} folder")
                return True
            else:
                respond_jarvis(f"Sorry, I couldn't find the {folder_name} folder.")
                return True

    return False


# Function to open specific files (same as before)
def open_file(query):
    file_paths = {
        "resume": "C:/Users/YourUsername/Documents/Resume.docx",
        "project report": "C:/Users/YourUsername/Documents/ProjectReport.pdf",
        "presentation": "C:/Users/YourUsername/Documents/Presentation.pptx"
    }

    for file_name, path in file_paths.items():
        if file_name in query.lower():
            if os.path.exists(path):
                subprocess.run(['start', path], shell=True)
                respond_jarvis(f"Opening {file_name}")
                return True
            else:
                respond_jarvis(f"Sorry, I couldn't find the {file_name}.")
                return True

    return False


# Function to search for information online (same as before)
def search_web(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    respond_jarvis(f"Searching the web for {query}")
    return True

def open_website(query):
    query_lower = query.lower()

    # Check if user is asking for weather forecast
    if "weather" in query_lower:
        words = query_lower.split()
        for i, word in enumerate(words):
            if word == "in" and i + 1 < len(words):
                city = words[i + 1]
                forecast = get_weather_forecast(city)
                respond_jarvis(forecast)
                return True

    # Handle popular websites
    if "open google" in query_lower:
        webbrowser.open("https://www.google.com")
        respond_jarvis("Opening Google")
        return True
    elif "open youtube" in query_lower:
        webbrowser.open("https://www.youtube.com")
        respond_jarvis("Opening YouTube")
        return True
    elif "open facebook" in query_lower:
        webbrowser.open("https://www.facebook.com")
        respond_jarvis("Opening Facebook")
        return True
    elif "open twitter" in query_lower:
        webbrowser.open("https://www.twitter.com")
        respond_jarvis("Opening Twitter")
        return True
    elif "open instagram" in query_lower:
        webbrowser.open("https://www.instagram.com")
        respond_jarvis("Opening Instagram")
        return True

    # General case for other websites
    words = query_lower.split()
    for word in words:
        if "." in word:  # If the query includes a domain (like .com, .org)
            url = f"https://{word}" if not word.startswith("http") else word
            webbrowser.open(url)
            respond_jarvis(f"Opening {word}")
            return True

    return False

    # General case for other websites
    words = query_lower.split()
    for word in words:
        if "." in word:
            url = f"https://{word}" if not word.startswith("http") else word
            webbrowser.open(url)
            respond_jarvis(f"Opening {word}")
            return True

    return False


def ask_jarvis():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected.")
            return ""

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio)
        print(f"User: {query}")
        return query
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return ""
    except sr.RequestError:
        print("Sorry, my speech service is down.")
        return ""


def call_openai_api(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}],
            max_tokens=50
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.RateLimitError:
        print("Rate limit exceeded. Please wait.")
        time.sleep(10)
        return "I'm currently over my rate limit. Please try again later."


def main():
    print("Hello! I am Jarvis. How can I assist you today?")

    while True:
        query = ask_jarvis()

        if query.lower() == 'Goodbye':
            respond_jarvis("Goodbye sir!")
            break

        if open_folder(query):
            continue

        if open_file(query):
            continue

        if open_website(query):
            continue

        if "search for" in query.lower() or "who is" in query.lower() or "what is" in query.lower():
            search_web(query)
            continue

        response = call_openai_api(query)
        respond_jarvis(response)


if __name__ == "__main__":
    main()
