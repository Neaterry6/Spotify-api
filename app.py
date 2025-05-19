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

# New lyrics route using YouTube auto subtitles
@app.get("/lyrics")
def lyrics(song: str = Query(...)):
    try:
        search_url = f"ytsearch1:{song} lyrics"
        output_path = "%(title)s.%(ext)s"

        # Download auto subtitles only
        cmd = [
            "yt-dlp", "--cookies", COOKIES, "--write-auto-sub", "--sub-lang", "en",
            "--skip-download", "-o", output_path, search_url
        ]
        subprocess.run(cmd, check=True)

        # Find the .vtt file
        vtt_file = next((f for f in os.listdir() if f.endswith(".en.vtt")), None)
        if not vtt_file:
            return {"lyrics": "No subtitles/lyrics found for this song."}

        # Parse the .vtt file
        def parse_vtt(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            text = ""
            for line in lines:
                if "-->" not in line and line.strip() != "" and not line.strip().startswith("WEBVTT"):
                    text += line.strip() + " "
            return text.strip()

        lyrics_text = parse_vtt(vtt_file)

        # Clean up downloaded .vtt file
        os.remove(vtt_file)

        return {"lyrics": lyrics_text}
    except Exception as e:
        return {"lyrics": f"Error: {e}"}