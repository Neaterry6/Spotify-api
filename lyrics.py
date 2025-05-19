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
        lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})
        if lyrics_divs:
            lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])
            return lyrics
        return "Lyrics found but could not parse."
    except Exception as e:
        return f"Error fetching lyrics: {str(e)}"
