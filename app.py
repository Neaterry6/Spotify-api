from fastapi import FastAPI, Query, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import requests
import aiofiles
import subprocess
import asyncio
import os
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io

app = FastAPI()

COOKIES = "cookies.txt"
API_KEY = "423c0305-cf71-48dc-b57f-693399ce53d1"
API_BASE = "https://kaiz-apis.gleeze.com/api/gpt-3.5"

# Run subprocess asynchronously
async def run_command(cmd):
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout, stderr, process.returncode

# Download audio from YouTube
@app.get("/play")
async def play(song: str = Query(...)):
    search_url = f"ytsearch1:{song}"
    output_path = "audio.%(ext)s"
    cmd = ["yt-dlp", "--cookies", COOKIES, "-x", "--audio-format", "mp3", "-o", output_path, search_url]

    stdout, stderr, exit_code = await run_command(cmd)
    if exit_code != 0:
        return {"error": stderr.decode()}

    mp3_file = next((f for f in os.listdir() if f.endswith(".mp3")), None)
    return FileResponse(mp3_file, media_type="audio/mpeg", filename=mp3_file) if mp3_file else {"error": "Download failed."}

# Download video from YouTube
@app.get("/video")
async def video(search: str = Query(...)):
    search_url = f"ytsearch1:{search}"
    output_path = "video.%(ext)s"
    cmd = ["yt-dlp", "--cookies", COOKIES, "-f", "mp4", "-o", output_path, search_url]

    stdout, stderr, exit_code = await run_command(cmd)
    if exit_code != 0:
        return {"error": stderr.decode()}

    video_file = next((f for f in os.listdir() if f.endswith(".mp4")), None)
    return FileResponse(video_file, media_type="video/mp4", filename=video_file) if video_file else {"error": "Download failed."}

# Scrape lyrics without API key
@app.get("/lyrics")
def lyrics(song: str = Query(...)):
    search_url = f"https://www.lyrics.com/serp.php?st={song.replace(' ', '+')}"
    response = requests.get(search_url)
    if response.status_code != 200:
        return {"error": "Lyrics site unreachable."}

    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_div = soup.find("pre", class_="lyric-body")
    return {"lyrics": lyrics_div.text.strip() if lyrics_div else "Lyrics not found."}

# Chatbot that sends actual image files instead of links
@app.api_route("/chat", methods=["GET", "POST"])
async def chat(prompt: str = Query(None), prompt_form: str = Form(None), background_tasks: BackgroundTasks = None):
    try:
        prompt_value = prompt or prompt_form
        if not prompt_value:
            return {"error": "No prompt provided."}

        params = {"q": prompt_value, "apikey": API_KEY}
        response = requests.get(API_BASE, params=params)
        data = response.json()

        if "image" in data:
            image_url = data["image"]
            image_response = requests.get(image_url)
            file_name = "generated_image.jpg"
            
            async with aiofiles.open(file_name, "wb") as f:
                await f.write(image_response.content)

            return FileResponse(file_name, media_type="image/jpeg", filename=file_name)
        else:
            return {"response": data.get("response", "Sorry, no reply from API.")}
    except Exception as e:
        return {"error": str(e)}

# Extract text from uploaded image
@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image).strip()
        return {"extracted_text": text if text else "No text found in the image."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})