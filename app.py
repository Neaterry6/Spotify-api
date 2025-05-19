from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess, os, requests
from bs4 import BeautifulSoup

app = FastAPI()

COOKIES = "cookies.txt"

# Download audio from YouTube
@app.get("/play")
def play(song: str = Query(...)):
    try:
        search_url = f"ytsearch1:{song}"
        output_path = "audio.%(ext)s"
        cmd = [
            "yt-dlp", "--cookies", COOKIES, "-x", "--audio-format", "mp3",
            "-o", output_path, search_url
        ]
        subprocess.run(cmd, check=True)
        mp3_file = next((f for f in os.listdir() if f.endswith(".mp3")), None)
        if mp3_file:
            return FileResponse(mp3_file, media_type="audio/mpeg", filename=mp3_file)
        return {"result": "Audio download failed."}
    except Exception as e:
        return {"result": f"Error: {e}"}

# Download video from YouTube
@app.get("/video")
def video(search: str = Query(...)):
    try:
        search_url = f"ytsearch1:{search}"
        output_path = "video.%(ext)s"
        cmd = [
            "yt-dlp", "--cookies", COOKIES, "-f", "mp4", "-o", output_path, search_url
        ]
        subprocess.run(cmd, check=True)
        video_file = next((f for f in os.listdir() if f.endswith(".mp4")), None)
        if video_file:
            return FileResponse(video_file, media_type="video/mp4", filename=video_file)
        return {"result": "Video download failed."}
    except Exception as e:
        return {"result": f"Error: {e}"}

# Fetch lyrics from Genius
@app.get("/lyrics")
def lyrics(song: str = Query(...)):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        search_url = f"https://genius.com/api/search/multi?per_page=1&q={song}"
        res = requests.get(search_url, headers=headers)
        if res.status_code == 403:
            return {"lyrics": "Error: Genius blocked access (403)"}
        response = res.json()
        hits = response['response']['sections'][0]['hits']
        if not hits:
            return {"lyrics": "Lyrics not found."}
        song_path = hits[0]['result']['path']
        song_url = f"https://genius.com{song_path}"
        page = requests.get(song_url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        lyrics_tag = soup.find("div", {"data-lyrics-container": "true"})
        if lyrics_tag:
            lyrics = lyrics_tag.get_text(separator="\n")
            return {"lyrics": lyrics}
        return {"lyrics": "Lyrics found but could not parse."}
    except Exception as e:
        return {"lyrics": f"Error: {e}"}