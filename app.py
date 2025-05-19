from fastapi import FastAPI
from lyrics import get_lyrics
from downloader import download_song
from concurrent.futures import ThreadPoolExecutor
import asyncio

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Spotify API running"}

@app.get("/lyrics")
async def lyrics(song: str):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, get_lyrics, song)
    return {"lyrics": result}

@app.get("/play")
async def play(song: str):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, download_song, song)
    return {"result": result}
