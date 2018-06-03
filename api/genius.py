from __future__ import print_function
from config import Config

import base64
import json
import requests
import sys
from bs4 import BeautifulSoup

try:
    import urllib.request, urllib.error
    import urllib.parse as urllibparse
except ImportError:
    import urllib as urllibparse

# ----------------- 0. GENIUS BASE URL ----------------

GENIUS_API_BASE_URL = "http://api.genius.com"

# ----------------- 1. AUTH ----------------

# Token
ACCESS_TOKEN = Config.TOKEN

# Auth Header
AUTH_HEADER = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

# ----------------- 2. SEARCH ----------------
# https://docs.genius.com/#!#%2Fauthentication-h1

def search(query):
    url = f'{GENIUS_API_BASE_URL}/search?q={query}'
    resp = requests.get(url, headers=AUTH_HEADER)

    return resp.json()

# ----------------- 3. GET SONG ----------------
# https://docs.genius.com/#songs-h2

def get_song(song_id):
    url = f'{GENIUS_API_BASE_URL}/songs/{song_id}'
    resp = requests.get(url, headers=AUTH_HEADER)

    return resp.json()

# ----------------- 4. GET LYRICS ----------------
# This is not part of the API, Genius doesn't give us it from the API
# so we gotta go scrape their webpage ;)

def scrape_genius(song):
    page_url = "http://genius.com/{}".format(song['response']['song']['path'])
    page     = requests.get(page_url)
    html     = BeautifulSoup(page.text, "html.parser")
   
    [h.extract() for h in html('script')]  # remove script tags that they put in the middle of the lyrics
    
    lyrics = html.find("div", class_="lyrics").get_text() # updated css where the lyrics are based in HTML
    return lyrics.replace('\n', '')

def get_lyrics(song_title, artist_name):
    song_info   = None
    search_resp = search(song_title)

    for hit in search_resp.json()['response']['hits']:
        if hit["result"]["primary_artist"]["name"] == artist_name:
            song_info = hit
            break
    
    if not song_info: return {'error': {'status': '404', 'message': 'song not found'}}

    song = get_song(song_info['result']['id'])
    return scrape_genius(song)
