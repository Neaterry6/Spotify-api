import json
import os
import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from time import time

app = Flask(__name__)

CACHE_FILE = 'cache.json'

# Load or init cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE) as f:
        cache = json.load(f)
else:
    cache = {}

# Helper: Save cache
def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

# Read cookies from cookies.txt (Netscape format)
def load_cookies():
    cookies = {}
    with open('cookies.txt') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) == 7:
                domain, _, path, secure, expiry, name, value = parts
                cookies[name] = value
    return cookies

cookies = load_cookies()

# Fetch lyrics from lyrics.ovh
def fetch_lyrics(artist, title):
    try:
        url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
        res = requests.get(url)
        data = res.json()
        if 'lyrics' in data and data['lyrics'].strip():
            return data['lyrics']
    except:
        pass
    return None

# Scrape Spotify track page for info and playable URL
def scrape_spotify(track_id):
    url = f"https://open.spotify.com/track/{track_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0',
    }
    res = requests.get(url, cookies=cookies, headers=headers)
    if res.status_code != 200:
        return None
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Example: scrape title and artist from meta tags or page content
    title = None
    artist = None
    for meta in soup.find_all('meta'):
        if meta.get('property') == 'og:title':
            title = meta.get('content')
        elif meta.get('property') == 'music:musician':
            artist = meta.get('content')
    if not title or not artist:
        # fallback parsing if needed
        pass

    # Spotify does not provide direct mp3 links; best you can do is return preview_url or embed URL
    # Let's try to get preview URL from Spotify public API (no auth)
    api_url = f"https://api.spotify.com/v1/tracks/{track_id}"
    api_res = requests.get(api_url)
    preview_url = None
    if api_res.status_code == 200:
        data = api_res.json()
        preview_url = data.get('preview_url')
    
    return {
        'title': title,
        'artist': artist,
        'preview_url': preview_url,
        'track_url': url
    }

@app.route('/lyrics')
def lyrics():
    track_id = request.args.get('track_id')
    if not track_id:
        return jsonify({'error': 'track_id parameter required'}), 400

    if track_id in cache and 'lyrics' in cache[track_id]:
        return jsonify({'lyrics': cache[track_id]['lyrics']})

    info = scrape_spotify(track_id)
    if not info or not info.get('artist') or not info.get('title'):
        return jsonify({'error': 'Failed to get song info'}), 404

    lyrics = fetch_lyrics(info['artist'], info['title'])
    if not lyrics:
        lyrics = "Lyrics not found."

    cache.setdefault(track_id, {})['lyrics'] = lyrics
    save_cache()

    return jsonify({'lyrics': lyrics})

@app.route('/play')
def play():
    track_id = request.args.get('track_id')
    if not track_id:
        return jsonify({'error': 'track_id parameter required'}), 400
    
    if track_id in cache and 'preview_url' in cache[track_id]:
        return jsonify({'preview_url': cache[track_id]['preview_url']})

    info = scrape_spotify(track_id)
    if not info or not info.get('preview_url'):
        return jsonify({'error': 'No playable URL found'}), 404

    cache.setdefault(track_id, {})['preview_url'] = info['preview_url']
    save_cache()

    return jsonify({'preview_url': info['preview_url']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000
