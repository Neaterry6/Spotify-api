import requests
from bs4 import BeautifulSoup

def get_lyrics(song_name):
    try:
        search_url = f"https://genius.com/api/search/multi?per_page=1&q={song_name}"
        response = requests.get(search_url).json()
        hits = response['response']['sections'][0]['hits']
        if not hits:
            return "Lyrics not found."
        song_path = hits[0]['result']['path']
        song_url = f"https://genius.com{song_path}"
        page = requests.get(song_url)
        soup = BeautifulSoup(page.text, "html.parser")
        lyrics = soup.find("div", {"data-lyrics-container": "true"})
        if lyrics:
            return lyrics.get_text(separator="\n")
        return "Lyrics found but could not parse."
    except Exception as e:
        return f"Error fetching lyrics: {str(e)}"
