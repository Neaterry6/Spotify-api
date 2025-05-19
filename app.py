from fastapi import FastAPI, Query
from downloader import download_song
from lyrics import get_lyrics

app = FastAPI()

@app.get("/download")
def download_endpoint(q: str = Query(..., description="Song name")):
    result = download_song(q)
    return result

@app.get("/lyrics")
def lyrics_endpoint(q: str = Query(..., description="Song name")):
    lyrics = get_lyrics(q)
    return {"lyrics": lyrics
