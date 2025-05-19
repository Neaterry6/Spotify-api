from fastapi import FastAPI, HTTPException
from lyrics import get_lyrics
from downloader import download_song
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/lyrics/")
async def lyrics_endpoint(song: str):
    try:
        lyrics = await get_lyrics(song)
        return {"lyrics": lyrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lyrics: {str(e)}")

@app.get("/play/")
async def play_song(song: str):
    try:
        filepath = await download_song(song)
        return FileResponse(filepath, media_type="audio/mpeg", filename=f"{song}.mp3")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error playing song: {str(e)}")
