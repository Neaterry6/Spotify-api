import requests
from bs4 import BeautifulSoup

def get_lyrics(song_name):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        search_url = f"https://genius.com/api/search/multi?per_page=1&q={song_name}"
        response = requests.get(search_url, headers=headers)
        
        if response.status_code != 200:
            return f"Error fetching lyrics: Genius API responded with status {response.status_code}"
        
        data = response.json()
        hits = data['response']['sections'][0]['hits']
        
        if not hits:
            return "Lyrics not found."

        song_path = hits[0]['result']['path']
        song_url = f"https://genius.com{song_path}"
        page = requests.get(song_url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})

        if not lyrics_divs:
            return "Lyrics found but could not parse."

        lyrics = "\n".join(div.get_text(separator="\n") for div in lyrics_divs)
        return lyrics.strip()

    except Exception as e:
        return f"Error fetching lyrics: {str(e)}"
