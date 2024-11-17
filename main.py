import speech_recognition as sr
import os
import pyttsx3
import webbrowser
import openai
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import quote


CLIENT_ID = '7aa35fc449fd471eaf1983d1bea6431d'
CLIENT_SECRET = 'd5b68f1988604c7b9590fec3f15a93e5'
REDIRECT_URI = 'http://localhost:8888/callback'

scope = 'user-read-playback-state user-modify-playback-state'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))


def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def search_and_play_song(song_name):
    results = sp.search(q=song_name, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        print(f"Playing: {track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")

        devices = sp.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            sp.start_playback(device_id=device_id, uris=[track_uri])
        else:
            print("No active devices found. Please start Spotify on a device.")
    else:
        print("Song not found. Please try again.")


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source)
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I could not understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return ""



def open_google_maps(location=None, destination=None):
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://www.google.com/maps")
    time.sleep(5)

    if location:
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(location)
        search_box.send_keys(Keys.RETURN)
        say(f"Searching for {location} on Google Maps.")
        print(f"Searching for: {location}")
        time.sleep(5)

    if destination:
        try:
            directions_button = driver.find_element(By.XPATH, '//button[@aria-label="Directions"]')
            directions_button.click()
            time.sleep(3)
            destination_input = driver.find_element(By.XPATH, '//input[@aria-label="Choose starting point, or click on the map..."]')
            destination_input.send_keys(destination)
            destination_input.send_keys(Keys.RETURN)
            say(f"Getting directions to {destination}.")
            print(f"Getting directions to: {destination}")
            time.sleep(5)
        except Exception as e:
            say("Could not fetch directions.")
            print(f"Error fetching directions: {e}")

    return driver

def search_nearby_places(driver, place_type):
    """Searches for nearby places like restaurants or hospitals."""
    try:
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(place_type + " near me")
        search_box.send_keys(Keys.RETURN)
        speak(f"Searching for nearby {place_type}.")
        time.sleep(5)
    except Exception as e:
        speak(f"Could not search for nearby {place_type}.")
        print(f"Error: {e}")

def fetch_current_location(driver):
    """Fetches and announces the current location using Google Maps."""
    try:
        # Locate and click the 'Current location' button
        current_location_button = driver.find_element(By.XPATH, '//*[@aria-label="Current location"]')
        current_location_button.click()
        speak("Fetching your current location...")
        time.sleep(5)

        # Extract location from the visible map area
        location_name = driver.find_element(By.XPATH, '//*[@class="section-hero-header-title"]')
        print(f"Current Location: {location_name.text}")
        speak(f"Your current location is {location_name.text}.")
    except Exception as e:
        speak("Unable to fetch your current location.")
        print(f"Error fetching current location: {e}")


def search_google(query):
    query = query.replace("google", "").strip()
    print(f"Searching Google for: {query}")
    google_url = f"https://www.google.com/search?q={quote(query)}"
    webbrowser.open(google_url)



import wikipedia

def search_wikipedia(query):
    query = query.replace("wikipedia", "").strip()
    if not query:
        say("Sorry, I didn't catch the query for Wikipedia.")
        print("Query is empty or invalid.")
        return

    print(f"Searching Wikipedia for: {query}")
    try:
        summary = wikipedia.summary(query, sentences=3)  # Fetch a brief summary
        say(f"Here's a brief summary from Wikipedia.")
        print(f"Summary for {query}:\n{summary}")
        say(summary)
    except wikipedia.exceptions.DisambiguationError as e:
        say("The term is ambiguous, please be more specific.")
        print(f"Disambiguation error: {e.options}")
    except wikipedia.exceptions.PageError:
        say("No Wikipedia page found for that query.")
        print(f"No Wikipedia page found for: {query}")
    except Exception as e:
        say("An error occurred while fetching the Wikipedia summary.")
        print(f"Unexpected error: {e}")



def search_youtube(query):
    # Initialize the Chrome driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        # Open YouTube
        driver.get("https://www.youtube.com")
        time.sleep(3)  # Wait for the page to load

        # Find the search bar and enter the query
        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for the search results to load

        # Click on the first video
        first_video = driver.find_element(By.XPATH, '(//ytd-video-renderer//a[@id="thumbnail"])[1]')
        first_video.click()
        print(f"Playing the first video for search: {query}")
        time.sleep(5)  # Let the video play for a while
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Keep the browser open for the user to watch the video
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    say("Hello, I am Jarvis A.I")
    while True:
        query = takeCommand().lower()
        if "search" in query:
            location = query.replace("search", "").strip()
            open_google_maps(location=location)
        elif "navigate to" in query:
            destination = query.replace("navigate to", "").strip()
            open_google_maps(destination=destination)
        elif "exit" in query or "quit" in query:
            say("Goodbye!")
            print("Exiting...")
            break
        elif "play song" in query:
            song_name = query.replace("play song", "").strip()
            search_and_play_song(song_name)
        elif "google" in query:
            search_google(query)
        elif "wikipedia" in query:
            search_wikipedia(query)
        elif "youtube" in query:
            search_youtube(query)
        elif "open music" in query:
            musicPath = "C:\\Users\\Laksh seth\\Downloads\\TOKYO MACHINE, NEFFEX - Desperate [NCS Release].mp3"
            os.startfile(musicPath)
        elif "find nearby" in query.lower():
            place_type = query.replace("find nearby", "").strip()
            driver = open_google_maps()
            search_nearby_places(driver, place_type)
        elif "where am i" in query:
            driver = open_google_maps()
            fetch_current_location(driver)
        elif "stop" in query.lower():
            break

